# dialer_app/services/google_stt_service.py
import asyncio
import queue
from google.cloud import speech
from google.cloud.speech import StreamingRecognizeRequest, StreamingRecognitionConfig, RecognitionConfig

class GoogleSTTService:
    def __init__(self, call_id, track, broadcast_callback, loop=None):
        """
        call_id: The Twilio call SID.
        track: "inbound" or "outbound"
        broadcast_callback: async function(call_id, transcript, track)
        loop: The main event loop to schedule coroutine calls.
        """
        self.call_id = call_id
        self.track = track
        self.broadcast_callback = broadcast_callback
        self.active = True
        # Use a thread-safe blocking queue to store audio chunks
        self.audio_queue = queue.Queue()
        self.client = speech.SpeechClient()
        self.streaming_config = StreamingRecognitionConfig(
            config=RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.MULAW,
                sample_rate_hertz=8000,
                language_code="en-US",
                enable_automatic_punctuation=True,
            ),
            interim_results=False,
        )
        # Capture the main event loop (from the main thread)
        self.loop = loop or asyncio.get_event_loop()

    def request_generator(self):
        """Generator that yields audio chunks as StreamingRecognizeRequest objects."""
        while self.active:
            try:
                # Wait up to 1 second for an audio chunk
                audio_chunk = self.audio_queue.get(timeout=1)
                yield StreamingRecognizeRequest(audio_content=audio_chunk)
            except queue.Empty:
                continue

    def _streaming_recognize(self):
        """Blocking function to call Google STT streaming API."""
        try:
            responses = self.client.streaming_recognize(self.streaming_config, self.request_generator())
            for response in responses:
                for result in response.results:
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript.strip()
                        if transcript:
                            print(f"[GoogleSTTService] Transcript found: {transcript}")
                            # Schedule broadcast on the main event loop
                            future = asyncio.run_coroutine_threadsafe(
                                self.broadcast_callback(self.call_id, transcript, self.track),
                                self.loop
                            )
                            try:
                                future.result()  # Optionally wait for completion
                            except Exception as ex:
                                print(f"[GoogleSTTService] Error broadcasting transcript: {ex}")
        except Exception as e:
            print(f"[GoogleSTTService] Error during streaming recognition for call {self.call_id}, track={self.track}: {e}")

    async def connect(self):
        """Starts the streaming recognition in a background thread."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._streaming_recognize)

    async def send_audio(self, audio_chunk):
        """Receives an audio chunk (bytes) and adds it to the queue."""
        if self.active and audio_chunk:
            self.audio_queue.put(audio_chunk)

    async def close(self):
        """Closes the streaming session."""
        self.active = False
