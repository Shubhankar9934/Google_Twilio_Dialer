# dialer_app/services/twilio_service.py
import os
from twilio.rest import Client
from dialer_app.config import Config

def initiate_outbound_call(caller_number, receiver_number):
    account_sid = Config.TWILIO_ACCOUNT_SID
    auth_token = Config.TWILIO_AUTH_TOKEN
    twilio_number = Config.TWILIO_PHONE_NUMBER

    ngrok_url = os.environ.get("NGROK_URL")
    if not ngrok_url:
        raise RuntimeError("Ngrok URL not found. Ensure ngrok is running and NGROK_ENABLED is True.")

    domain = ngrok_url.replace('https://', '').replace('http://', '').strip('/')
    stream_url = f"wss://{domain}/twilio"
    print(f"[Twilio Service] Using Media Stream URL: {stream_url}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Start>
        <Stream url="{stream_url}" track="both_tracks" />
    </Start>
    <Dial>{receiver_number}</Dial>
</Response>"""

    client = Client(account_sid, auth_token)
    call = client.calls.create(
        twiml=twiml,
        to=caller_number,
        from_=twilio_number
    )
    print("Outbound call initiated. SID:", call.sid)
    return call.sid
