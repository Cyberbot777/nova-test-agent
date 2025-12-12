import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Send, Trash2, X, AlertCircle, Volume2 } from 'lucide-react';

/**
 * Voice Chat Interface for Nova Agent
 * 
 * TODO - AUDIO INTEGRATION NEEDED:
 * 1. Add microphone recording (MediaRecorder API)
 * 2. Stream audio to backend via WebSocket
 * 3. Receive and play audio responses from Nova
 * 4. Handle bidirectional audio streaming
 * 
 * CURRENTLY: Just does text streaming (copied from test-frontend)
 * NEEDS: Audio capture, audio playback, WebSocket audio streaming
 */

const VoiceChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  
  // Audio refs (for future implementation)
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  
  // Typing animation state
  const [isTyping, setIsTyping] = useState(false);
  const bufferedTextRef = useRef('');
  const displayedLengthRef = useRef(0);
  const typingIntervalRef = useRef(null);
  const streamEndedRef = useRef(false);
  
  const TYPING_SPEED = 7;
  const TYPING_INTERVAL = 70;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Typing animation effect
  useEffect(() => {
    if (isTyping) {
      typingIntervalRef.current = setInterval(() => {
        const bufferedText = bufferedTextRef.current;
        const currentLength = displayedLengthRef.current;

        if (currentLength < bufferedText.length) {
          const nextLength = Math.min(currentLength + TYPING_SPEED, bufferedText.length);
          displayedLengthRef.current = nextLength;
          const displayedText = bufferedText.substring(0, nextLength);
          
          setMessages(prev => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg?.role === 'assistant') {
              lastMsg.content = displayedText;
            }
            return updated;
          });
        } else if (streamEndedRef.current && currentLength >= bufferedText.length) {
          setIsTyping(false);
          clearInterval(typingIntervalRef.current);
          typingIntervalRef.current = null;
        }
      }, TYPING_INTERVAL);
    }

    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
    };
  }, [isTyping]);

  // TODO: Implement audio recording
  const startRecording = async () => {
    try {
      // PLACEHOLDER - Needs implementation
      console.warn('Audio recording not yet implemented');
      console.log('TODO: Request microphone access');
      console.log('TODO: Start MediaRecorder');
      console.log('TODO: Stream audio chunks to backend');
      
      setError('Audio recording not yet implemented - use text input for now');
      
      // Example of what's needed:
      // const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // const mediaRecorder = new MediaRecorder(stream);
      // mediaRecorderRef.current = mediaRecorder;
      // ... handle audio chunks ...
      
    } catch (err) {
      setError(`Microphone error: ${err.message}`);
    }
  };

  const stopRecording = () => {
    // PLACEHOLDER
    console.warn('Stop recording not yet implemented');
    setIsRecording(false);
  };

  // Text message sending (temporary until audio works)
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    // Reset typing animation
    bufferedTextRef.current = '';
    displayedLengthRef.current = 0;
    streamEndedRef.current = false;
    setIsTyping(false);

    try {
      // Call backend API (SSE streaming)
      const response = await fetch('/api/invoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input })
      });

      if (!response.ok) {
        throw new Error('Failed to invoke agent');
      }

      // Handle SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let firstChunk = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          streamEndedRef.current = true;
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6).trim();
            if (!data) continue;

            try {
              const parsed = JSON.parse(data);

              if (parsed.chunk) {
                bufferedTextRef.current += parsed.chunk;
                
                if (firstChunk) {
                  firstChunk = false;
                  setIsTyping(true);
                  setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
                }
              } else if (parsed.end) {
                streamEndedRef.current = true;
              } else if (parsed.error) {
                throw new Error(parsed.error);
              }
            } catch (parseError) {
              console.error('Parse error:', parseError);
            }
          }
        }
      }

    } catch (err) {
      setError(err.message);
      streamEndedRef.current = true;
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setError(null);
    setIsTyping(false);
    bufferedTextRef.current = '';
    displayedLengthRef.current = 0;
    streamEndedRef.current = false;
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.avatar}>
            <Volume2 size={24} />
          </div>
          <div>
            <h3 style={styles.title}>Nova Voice Agent</h3>
            <p style={styles.subtitle}>Streaming Voice Conversation (POC)</p>
          </div>
        </div>
        <button onClick={handleClear} style={styles.clearButton}>
          <Trash2 size={18} style={{ marginRight: '6px' }} />
          Clear Chat
        </button>
      </div>

      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            style={styles.errorBanner}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} style={styles.closeError}>
              <X size={20} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages */}
      <div style={styles.messagesContainer}>
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={msg.role === 'user' ? styles.userMessageWrapper : styles.assistantMessageWrapper}
            >
              <div style={msg.role === 'user' ? styles.userMessage : styles.assistantMessage}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={styles.loadingWrapper}>
            <div style={styles.loadingIndicator}>
              <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 1, repeat: Infinity }} style={styles.loadingDot} />
              <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 1, repeat: Infinity, delay: 0.2 }} style={styles.loadingDot} />
              <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 1, repeat: Infinity, delay: 0.4 }} style={styles.loadingDot} />
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={styles.inputContainer}>
        <div style={styles.inputWrapper}>
          {/* TODO: Replace with audio recording when implemented */}
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
            placeholder="Type your message... (Audio not yet implemented)"
            style={styles.textarea}
            rows={3}
            disabled={isLoading}
          />
          <div style={styles.buttonGroup}>
            {/* Mic button - placeholder */}
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              style={{
                ...styles.micButton,
                ...(isRecording && styles.micButtonActive),
                ...(isLoading && styles.buttonDisabled)
              }}
              title="Voice recording (not yet implemented)"
            >
              {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            
            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              style={{
                ...styles.sendButton,
                ...((!input.trim() || isLoading) && styles.buttonDisabled)
              }}
            >
              {isLoading ? (
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
                  <Volume2 size={20} />
                </motion.div>
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Styles
const styles = {
  container: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: '#0f172a',
  },
  header: {
    background: '#1e293b',
    padding: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottom: '1px solid #334155',
  },
  headerContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  avatar: {
    width: '48px',
    height: '48px',
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
  },
  title: {
    color: '#f8fafc',
    fontSize: '18px',
    margin: 0,
    fontWeight: '600',
  },
  subtitle: {
    color: '#94a3b8',
    fontSize: '12px',
    margin: 0,
  },
  clearButton: {
    background: '#dc2626',
    color: 'white',
    border: 'none',
    padding: '10px 16px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
  },
  errorBanner: {
    background: '#991b1b',
    color: '#fecaca',
    padding: '14px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  closeError: {
    background: 'none',
    border: 'none',
    color: '#fecaca',
    cursor: 'pointer',
    padding: '4px',
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  userMessageWrapper: {
    display: 'flex',
    justifyContent: 'flex-end',
  },
  assistantMessageWrapper: {
    display: 'flex',
    justifyContent: 'flex-start',
  },
  userMessage: {
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: 'white',
    padding: '12px 16px',
    borderRadius: '16px',
    maxWidth: '70%',
    wordBreak: 'break-word',
  },
  assistantMessage: {
    background: '#1e293b',
    color: '#e2e8f0',
    padding: '12px 16px',
    borderRadius: '16px',
    maxWidth: '70%',
    wordBreak: 'break-word',
    border: '1px solid #334155',
  },
  loadingWrapper: {
    display: 'flex',
    justifyContent: 'flex-start',
  },
  loadingIndicator: {
    display: 'flex',
    gap: '8px',
    padding: '12px',
    background: '#1e293b',
    borderRadius: '12px',
  },
  loadingDot: {
    width: '8px',
    height: '8px',
    background: '#667eea',
    borderRadius: '50%',
  },
  inputContainer: {
    padding: '20px',
    background: '#1e293b',
    borderTop: '1px solid #334155',
  },
  inputWrapper: {
    display: 'flex',
    gap: '12px',
    alignItems: 'flex-end',
  },
  textarea: {
    flex: 1,
    background: '#0f172a',
    border: '1px solid #334155',
    color: '#f8fafc',
    padding: '12px',
    borderRadius: '12px',
    fontSize: '14px',
    resize: 'none',
    outline: 'none',
  },
  buttonGroup: {
    display: 'flex',
    gap: '8px',
  },
  micButton: {
    background: '#ef4444',
    color: 'white',
    border: 'none',
    width: '48px',
    height: '48px',
    borderRadius: '12px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  micButtonActive: {
    background: '#dc2626',
    animation: 'pulse 1s infinite',
  },
  sendButton: {
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: 'white',
    border: 'none',
    width: '48px',
    height: '48px',
    borderRadius: '12px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    background: '#334155',
    cursor: 'not-allowed',
  },
};

export default VoiceChat;

