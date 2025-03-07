# dialer_app/services/websocket_service.py
import base64
import asyncio
import json
from dialer_app.services.google_stt_service import GoogleSTTService

class WebSocketManager:
    def __init__(self):
        # Mapping: call_id -> {
        #   "inbound_service": GoogleSTTService,
        #   "outbound_service": GoogleSTTService,
        #   "inbound_task": asyncio.Task,
        #   "outbound_task": asyncio.Task,
        #   "clients": set(),
        #   "transcribe_enabled": bool
        # }
        self.active_calls = {}

    def enable_transcription_for_call(self, call_id: str) -> bool:
        call_data = self.active_calls.get(call_id)
        if not call_data:
            return False
        call_data["transcribe_enabled"] = True
        print(f"[WebSocketManager] Transcription enabled for call {call_id}")
        return True

    async def handle_twilio_media(self, websocket):
        call_id = None
        try:
            print("[WebSocketManager] Twilio WebSocket connection established")
            handshake = await websocket.receive_text()
            print(f"[WebSocketManager] Received handshake: {handshake}")

            async for message in websocket.iter_text():
                data = json.loads(message)
                event = data.get("event", "")
                if event == "start":
                    call_id = data["start"]["callSid"]
                    print(f"[WebSocketManager] Twilio stream START for call {call_id}")
                    if call_id not in self.active_calls:
                        current_loop = asyncio.get_running_loop()  # Capture the main event loop
                        inbound_service = GoogleSTTService(call_id, "inbound", self.broadcast_transcript, loop=current_loop)
                        outbound_service = GoogleSTTService(call_id, "outbound", self.broadcast_transcript, loop=current_loop)
                        inbound_task = asyncio.create_task(inbound_service.connect())
                        outbound_task = asyncio.create_task(outbound_service.connect())
                        self.active_calls[call_id] = {
                            "inbound_service": inbound_service,
                            "outbound_service": outbound_service,
                            "inbound_task": inbound_task,
                            "outbound_task": outbound_task,
                            "clients": set(),
                            "transcribe_enabled": False
                        }
                elif event == "media":
                    if call_id in self.active_calls:
                        call_data = self.active_calls[call_id]
                        if not call_data["transcribe_enabled"]:
                            continue
                        track = data["media"]["track"]
                        payload = data["media"]["payload"]
                        audio_data = base64.b64decode(payload)
                        if track == "inbound":
                            await call_data["inbound_service"].send_audio(audio_data)
                        elif track == "outbound":
                            await call_data["outbound_service"].send_audio(audio_data)
                elif event == "stop":
                    print(f"[WebSocketManager] Twilio stream STOP for call {call_id}")
                    await self.end_call(call_id)
        except Exception as e:
            print(f"[WebSocketManager] Error handling Twilio media: {e}")
        finally:
            if call_id:
                await self.end_call(call_id)

    async def broadcast_transcript(self, call_id, transcript, track):
        # This is now an async function to be scheduled properly by run_coroutine_threadsafe.
        await self._broadcast_transcript_async(call_id, transcript, track)

    async def _broadcast_transcript_async(self, call_id, transcript, track):
        call_data = self.active_calls.get(call_id)
        if not call_data:
            return
        message = {"transcript": transcript, "track": track}
        for client_ws in call_data["clients"]:
            try:
                await client_ws.send_json(message)
            except Exception as e:
                print(f"[WebSocketManager] Error sending transcript to client: {e}")

    async def end_call(self, call_id):
        call_data = self.active_calls.pop(call_id, None)
        if call_data:
            try:
                await call_data["inbound_service"].close()
                await call_data["outbound_service"].close()
                if not call_data["inbound_task"].done():
                    call_data["inbound_task"].cancel()
                    try:
                        await call_data["inbound_task"]
                    except asyncio.CancelledError:
                        pass
                if not call_data["outbound_task"].done():
                    call_data["outbound_task"].cancel()
                    try:
                        await call_data["outbound_task"]
                    except asyncio.CancelledError:
                        pass
                for client_ws in call_data["clients"]:
                    try:
                        await client_ws.send_json({"callEnded": True})
                    except:
                        pass
                print(f"[WebSocketManager] Call {call_id} ended and cleaned up.")
            except Exception as e:
                print(f"[WebSocketManager] Error during call cleanup: {e}")

    async def handle_client(self, websocket):
        current_call_id = None
        try:
            print("[WebSocketManager] Client WebSocket connection established")
            async for msg in websocket.iter_json():
                if "subscribe" in msg:
                    call_id = msg["subscribe"]
                    call_data = self.active_calls.get(call_id)
                    if call_data:
                        call_data["clients"].add(websocket)
                        current_call_id = call_id
                        await websocket.send_json({"transcript": f"Subscribed to call {call_id}"})
                    else:
                        await websocket.send_json({"error": f"Call {call_id} not found or not active"})
        except Exception as e:
            print(f"[WebSocketManager] handle_client error: {e}")
        finally:
            if current_call_id:
                call_data = self.active_calls.get(current_call_id)
                if call_data and websocket in call_data["clients"]:
                    call_data["clients"].remove(websocket)
