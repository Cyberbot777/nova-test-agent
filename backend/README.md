# Backend - DEPRECATED

**This Node.js backend is no longer used.**

The Nova Voice Agent now uses a Python backend.

## Use the Python Backend Instead

```bash
cd agent
python run_voice_server.py --port 8080
```

See `agent/README.md` for full instructions.

## Why Python?

The Amazon Nova Sonic bidirectional streaming API uses the `aws-sdk-bedrock-runtime` Python package, which provides the `invoke_model_with_bidirectional_stream` method. This is not available in the JavaScript AWS SDK.

## Files in This Folder

These files are kept for reference but are not used:
- `server.js` - Original placeholder Node.js server
- `package.json` - Node.js dependencies

The actual working backend is in `agent/nova_voice/`.
