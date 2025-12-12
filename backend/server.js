import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const AWS_REGION = process.env.AWS_REGION || 'us-east-1';
const NOVA_MODEL_ID = process.env.NOVA_MODEL_ID || 'amazon.nova-sonic-v2:0';

app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Nova Voice Backend',
    region: AWS_REGION,
    model: NOVA_MODEL_ID,
    ready: false,  // Set to true once Nova integration is complete
    message: 'Backend running - Nova integration pending'
  });
});

/**
 * PLACEHOLDER: Text invocation endpoint
 * TODO: Replace with audio streaming endpoint
 * 
 * Current: Simple text-based invocation (for testing)
 * Needed: Bidirectional audio streaming with Nova Sonic
 */
app.post('/api/invoke', async (req, res) => {
  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'Prompt required' });
  }

  console.log(`[Text Mode] Received prompt: ${prompt.substring(0, 50)}...`);

  // Set up SSE streaming
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  try {
    // TODO: Call Nova Sonic API here
    // For now, send a placeholder response
    
    const placeholderResponse = `[Nova Integration Pending]\n\nYou said: "${prompt}"\n\nTo complete this POC, we need to:\n1. Integrate with Nova Sonic API\n2. Handle audio input/output\n3. Implement bidirectional streaming\n\nSee README.md for research checklist.`;
    
    // Simulate streaming
    const words = placeholderResponse.split(' ');
    for (const word of words) {
      res.write(`data: ${JSON.stringify({ chunk: word + ' ' })}\n\n`);
      await new Promise(resolve => setTimeout(resolve, 50));
    }

    res.write(`data: ${JSON.stringify({ end: true })}\n\n`);
    res.end();

  } catch (error) {
    console.error('Error:', error);
    res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
    res.end();
  }
});

/**
 * PLACEHOLDER: WebSocket endpoint for audio streaming
 * TODO: Implement bidirectional audio streaming
 * 
 * This will need to:
 * 1. Accept audio chunks from frontend
 * 2. Stream audio to Nova Sonic
 * 3. Receive audio + text from Nova
 * 4. Stream both back to frontend
 */
const wss = new WebSocketServer({ noServer: true });

wss.on('connection', (ws) => {
  console.log('WebSocket client connected (audio streaming not yet implemented)');

  ws.on('message', (message) => {
    console.log('Received audio chunk (processing not yet implemented)');
    // TODO: Handle audio chunks
    // TODO: Send to Nova Sonic
    // TODO: Stream response back
    
    ws.send(JSON.stringify({
      error: 'Audio streaming not yet implemented',
      message: 'See README.md for Nova Sonic integration checklist'
    }));
  });

  ws.on('close', () => {
    console.log('WebSocket client disconnected');
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

// Start server
const server = app.listen(PORT, () => {
  console.log('\n=== Nova Voice Backend Server ===');
  console.log('═══════════════════════════════════════');
  console.log(`Server: http://localhost:${PORT}`);
  console.log(`Region: ${AWS_REGION}`);
  console.log(`Model: ${NOVA_MODEL_ID}`);
  console.log(`Status: Placeholder mode - Nova integration needed`);
  console.log('═══════════════════════════════════════');
  console.log('\nEndpoints:');
  console.log(`   GET  /api/health  - Health check`);
  console.log(`   POST /api/invoke  - Text invocation (placeholder)`);
  console.log(`   WS   (upgrade)    - Audio streaming (placeholder)`);
  console.log('\nNext Steps:');
  console.log('   1. Research Nova Sonic API specifications');
  console.log('   2. Implement audio streaming integration');
  console.log('   3. Test with frontend audio capture');
  console.log('   See README.md for full checklist\n');
});

// Handle WebSocket upgrade
server.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

