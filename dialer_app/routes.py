# dialer_app/routes.py
from fastapi import APIRouter, Request, Form, HTTPException, WebSocket, status
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dialer_app.services.twilio_service import initiate_outbound_call
from dialer_app.services.websocket_service import WebSocketManager

router = APIRouter()
websocket_manager = WebSocketManager()

class EnableTranscriptionRequest(BaseModel):
    call_sid: str

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="dialer_app/templates")
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/call")
async def start_call(caller: str = Form(...), receiver: str = Form(...)):
    if not caller or not receiver:
        raise HTTPException(status_code=400, detail="Caller or Receiver not specified")
    call_sid = initiate_outbound_call(caller, receiver)
    return JSONResponse({"status": "Call initiated", "call_sid": call_sid})

@router.post("/enable_transcription", status_code=status.HTTP_200_OK)
async def enable_transcription(payload: EnableTranscriptionRequest):
    call_sid = payload.call_sid
    success = websocket_manager.enable_transcription_for_call(call_sid)
    if not success:
        raise HTTPException(status_code=404, detail="Call not found or no active call")
    return {"message": "Transcription enabled", "call_sid": call_sid}

@router.websocket("/twilio")
async def twilio_websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket_manager.handle_twilio_media(websocket)

@router.websocket("/ws")
async def client_websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket_manager.handle_client(websocket)
