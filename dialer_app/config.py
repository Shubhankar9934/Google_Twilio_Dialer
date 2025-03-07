# dialer_app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

class Config:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    VERIFIED_CALLER_NUMBER = os.getenv("VERIFIED_CALLER_NUMBER")
    DEFAULT_RECEIVER_NUMBER = os.getenv("DEFAULT_RECEIVER_NUMBER")

    # Not needed anymore; using Google STT instead of Deepgram
    # DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

    NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
    NGROK_ENABLED = os.getenv("NGROK_ENABLED", "False").lower() == "true"

    AUDIO_ENCODING = "mulaw"
    SAMPLE_RATE = 8000
