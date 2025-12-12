# Nova Voice Backend

Express server for handling audio streaming between frontend and Nova Sonic API.

## Configuration

Create a `.env` file with:

```env
AWS_REGION=us-east-1
NOVA_MODEL_ID=amazon.nova-sonic-v2:0
PORT=3001
```

## Installation

```bash
npm install
```

## Running

```bash
npm start       # Production
npm run dev     # Development with auto-reload
```

## Current Status

**Placeholder Mode** - Text-only responses, audio integration pending

## Endpoints

- `GET /api/health` - Health check and configuration status
- `POST /api/invoke` - Text invocation (placeholder, returns mock response)
- WebSocket upgrade - Audio streaming (not yet implemented)

## TODO

See main README.md for Nova Sonic integration checklist.

