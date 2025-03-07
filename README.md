# Twilio Dialer Application

A sophisticated FastAPI-based dialer application that integrates Twilio for call handling and Google Speech-to-Text for real-time transcription.

## Features

- **Call Management**:
  - Handle outbound calls using Twilio
  - Route calls to specified receivers
  - Track call status and duration
  - Real-time call monitoring

- **Real-time Transcription**:
  - Live speech-to-text using Google Speech-to-Text API
  - Separate transcription for inbound and outbound audio
  - WebSocket-based real-time updates
  - Configurable transcription settings

- **Web Interface**:
  - Monitor active calls
  - View real-time transcriptions
  - Enable/disable transcription per call
  - WebSocket-based live updates

## Prerequisites

- Python 3.8 or higher
- Twilio account credentials:
  - Account SID
  - Auth Token
  - Twilio phone number
- Google Cloud credentials (service account key file)
- Ngrok for local development

## Setup

1. Clone the repository and navigate to the project directory:

```bash
cd dialer
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create environment configuration:

```bash
cp .env.example .env
```

5. Configure your `.env` file with the following credentials:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
NGROK_ENABLED=true
```

6. Set up Google Cloud credentials:
- Place your Google Cloud service account key file in the project directory
- Set environment variable:
```bash
set GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
```

## Running the Application

1. Start ngrok for local development:

```bash
ngrok http 8000
```

2. Copy the ngrok HTTPS URL and set it in your environment:

```bash
export NGROK_URL=your_ngrok_url
```

3. Start the application:

```bash
python run.py
```

The application will be available at http://localhost:8000

## System Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system architecture diagrams and flow explanations.

## WebSocket Communication

- `/twilio` endpoint: Handles media streams from Twilio
- Client WebSocket: Provides real-time transcription updates to web interface

## Development

Key components:

- `run.py`: Application entry point
- `config.py`: Configuration management
- `services/`:
  - `twilio_service.py`: Twilio integration
  - `google_stt_service.py`: Speech-to-text processing
  - `websocket_service.py`: WebSocket management
- `static/`: Frontend assets
- `templates/`: HTML templates

## Security Considerations

- Never commit `.env` file
- Implement proper webhook validation in production
- Use HTTPS in production
- Update Flask secret key in production
- Validate all incoming WebSocket connections
- Implement rate limiting for API endpoints
- Secure storage of API keys and tokens

## Error Handling

The application includes:
- Automatic retry logic for API calls
- WebSocket reconnection handling
- Graceful degradation of features
- Detailed error logging
- User-friendly error messages

## Monitoring

Monitor application health through:
- Console logs for system events
- WebSocket connection status
- Transcription service status
- Call state tracking

## Production Deployment

Additional steps for production:
1. Set up SSL/TLS certificates
2. Configure proper domain routing
3. Implement monitoring and logging
4. Set up error reporting
5. Configure backup systems
6. Implement proper security measures



set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\shubh\Desktop\Google_STT_Dialer\Dialer\call-analyzer-452421-efc670a5af68.json
