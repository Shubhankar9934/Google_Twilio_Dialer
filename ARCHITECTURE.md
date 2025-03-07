# System Architecture

## High-Level Overview

```mermaid
graph TB
    A[Web Interface] -->|WebSocket| B[FastAPI Application]
    B -->|Media Stream| C[Twilio Service]
    B -->|Streaming API| D[Google STT Service]
    C -->|Audio Stream| B
    D -->|Transcription| B
    B -->|Updates| A

    subgraph Web Layer
        A
    end
    
    subgraph Application Layer
        B
    end
    
    subgraph External Services
        C
        D
    end
```

## Call Flow

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web Interface
    participant F as FastAPI App
    participant T as Twilio
    participant G as Google STT

    U->>W: Initiate Call
    W->>F: Request Call
    F->>T: Create Call
    T-->>F: Call SID
    F->>W: Call Created
    
    T->>F: Media Stream Start
    
    par Track 1
        F->>G: Inbound Audio Stream
        G-->>F: Inbound Transcription
        F-->>W: Update UI
    and Track 2
        F->>G: Outbound Audio Stream
        G-->>F: Outbound Transcription
        F-->>W: Update UI
    end
    
    T->>F: Media Stream End
    F->>G: Close Connections
    F->>W: Call Ended
```

## WebSocket Management

```mermaid
graph TD
    A[WebSocket Manager] --> B[Twilio Media Handler]
    A --> C[Client Handler]
    
    B --> D[Inbound Service]
    B --> E[Outbound Service]
    
    D --> F[Google STT API]
    E --> F
    
    F --> G[Transcription]
    G --> C
    
    subgraph Active Calls
        H[Call ID]
        H --> I[Inbound Task]
        H --> J[Outbound Task]
        H --> K[Connected Clients]
    end
```

## Component Details

### WebSocket Manager
- Manages active call sessions
- Handles WebSocket connections from both Twilio and web clients
- Routes audio streams and transcriptions
- Maintains client subscriptions

### Google STT Service
- Handles real-time audio transcription
- Maintains streaming connection to Google Speech-to-Text API
- Processes both inbound and outbound audio tracks
- Uses queues for efficient audio chunk processing

### Twilio Service
- Initiates outbound calls
- Configures media streams
- Manages call routing
- Handles TwiML generation

## Data Flow

```mermaid
graph LR
    A[Audio Input] --> B[Twilio Media Stream]
    B --> C[WebSocket Manager]
    C --> D[Google STT Service]
    D --> E[Transcription]
    E --> F[Client WebSocket]
    F --> G[Web Interface]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
```

## Architecture Decisions

1. **WebSocket-based Communication**
   - Real-time audio streaming
   - Bi-directional communication
   - Low latency updates

2. **Service Separation**
   - Modular design
   - Independent scaling
   - Clear responsibility boundaries

3. **Async Processing**
   - Non-blocking operations
   - Efficient resource usage
   - Better scalability

4. **Track Separation**
   - Independent inbound/outbound processing
   - Isolated failure domains
   - Better monitoring capability
