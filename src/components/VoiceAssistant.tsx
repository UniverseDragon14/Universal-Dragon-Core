import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, User, Bot, Trash2, Database, Volume2, VolumeX, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { io } from 'socket.io-client';

interface Message {
  role: 'user' | 'assistant';
  text: string;
  timestamp?: number;
}

export const VoiceAssistant: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGptMode, setIsGptMode] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState<number | null>(null);
  const [memoryStatus, setMemoryStatus] = useState<'IDLE' | 'SAVING' | 'LOADED'>('IDLE');
  const scrollRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const savedMemory = localStorage.getItem('DRAGON_GRID_MEMORY');
    if (savedMemory) {
      try {
        const parsed = JSON.parse(savedMemory);
        setMessages(parsed);
        setMemoryStatus('LOADED');
        setTimeout(() => setMemoryStatus('IDLE'), 2000);
      } catch (e) {
        console.error('Failed to load memory:', e);
      }
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      setMemoryStatus('SAVING');
      localStorage.setItem('DRAGON_GRID_MEMORY', JSON.stringify(messages));
      setTimeout(() => setMemoryStatus('IDLE'), 1000);
    }
  }, [messages]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  useEffect(() => {
    const socket = io();
    socket.on('dragon_eye_detection', (det: any) => {
      if (det.confidence > 0.9 && !det.isMock) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          text: `[டிராகன் எச்சரிக்கை] மாஸ்டர் அஸ்லம், நான் ${det.camera} இல் ${Math.round(det.confidence * 100)}% நம்பிக்கையுடன் ஒரு ${String(det.object).toUpperCase()} ஐக் கண்டறிந்துள்ளேன்.`
        }]);
      }
    });
    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.lang = 'ta-IN';

    recognitionRef.current.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      const upperTranscript = transcript.toUpperCase();

      if (upperTranscript.includes('GPT') || upperTranscript.includes('ஜிபிடி')) {
        setIsGptMode(true);
        const query = transcript.replace(/^(GPT|ஜிபிடி)\s*/i, '').trim();
        if (query) {
          handleSendMessage(query, true);
        } else {
          setMessages(prev => [...prev,
            { role: 'user', text: transcript },
            { role: 'assistant', text: 'GPT_CORE_TRIGGERED: மாஸ்டர் அஸ்லம், Groq/OpenAI backend mode active. கட்டளையைச் சொல்லுங்கள்.' }
          ]);
        }
        setIsListening(false);
        return;
      }

      handleSendMessage(transcript);
      setIsListening(false);
    };

    recognitionRef.current.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setMessages(prev => [...prev, { role: 'assistant', text: 'மாஸ்டர் அஸ்லம், voice signal fail. Type pannunga, NOVA ready.' }]);
      setIsListening(false);
    };

    recognitionRef.current.onend = () => setIsListening(false);
  }, [messages]);

  const handleSendMessage = async (text: string, forceGptMode: boolean = false) => {
    if (!text.trim() || isLoading) return;

    const currentGptMode = forceGptMode || isGptMode;
    const userMessage: Message = { role: 'user', text, timestamp: Date.now() };
    const newMessages = [...messages, userMessage];

    setMessages(newMessages);
    setInputText('');
    setIsLoading(true);

    try {
      const history = newMessages.slice(-10, -1).map(msg => ({
        role: msg.role,
        content: msg.text
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentGptMode ? `[GPT_ENHANCED_MODE] ${text}` : text,
          history
        })
      });

      const data = await response.json();
      const assistantMessage: Message = {
        role: 'assistant',
        text: data?.text || 'NOVA brain reply empty. Backend check pannunga.',
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('NOVA API error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'NOVA backend connect aagala. Server-la GROQ_API_KEY / OPENAI_API_KEY check pannunga.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const speakMessage = (text: string, index: number) => {
    if (!window.speechSynthesis) return;

    if (isSpeaking === index) {
      window.speechSynthesis.cancel();
      setIsSpeaking(null);
      return;
    }

    window.speechSynthesis.cancel();
    setIsSpeaking(index);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ta-IN';
    utterance.rate = 0.92;
    utterance.pitch = 1.05;
    utterance.onend = () => setIsSpeaking(null);
    utterance.onerror = () => setIsSpeaking(null);
    window.speechSynthesis.speak(utterance);
  };

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      setIsListening(true);
      recognitionRef.current?.start();
    }
  };

  const clearMemory = () => {
    if (window.confirm('மாஸ்டர் அஸ்லம், NOVA local memory clear panna ok-aa?')) {
      localStorage.removeItem('DRAGON_GRID_MEMORY');
      setMessages([]);
    }
  };

  return (
    <div className="glass-panel p-4 flex flex-col gap-4 h-full relative overflow-hidden">
      <div className="flex items-center justify-between z-10">
        <h2 className="micro-label flex items-center gap-2 text-[#00FFFF]">
          <Bot className="w-4 h-4" /> DRAGON_ASSISTANT
        </h2>
        <div className="flex items-center gap-3">
          {isGptMode && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-1 bg-[#00FFFF]/10 border border-[#00FFFF]/30 px-1.5 py-0.5 rounded"
            >
              <Zap className="w-2 h-2 text-[#00FFFF]" />
              <span className="text-[7px] font-mono text-[#00FFFF]">GROQ_GPT120_MODE</span>
            </motion.div>
          )}
          <div className="flex items-center gap-1">
            <Database className={`w-3 h-3 ${memoryStatus === 'SAVING' ? 'text-[#FF3300] animate-pulse' : 'text-[#444]'}`} />
            <span className="text-[8px] font-mono text-[#444]">{memoryStatus}</span>
          </div>
          <span className={`text-[10px] font-mono ${isListening ? 'text-[#FF3300] animate-pulse' : 'text-[#444]'}`}>
            {isListening ? 'LISTENING...' : 'IDLE'}
          </span>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 bg-black border border-[#222] rounded p-3 overflow-y-auto font-mono text-[11px] space-y-4"
      >
        <AnimatePresence initial={false}>
          {messages.length === 0 && (
            <div className="text-[#444] text-center mt-10 italic">
              Groq/OpenAI backend ready. கட்டளைகளுக்காக காத்திருக்கிறேன், மாஸ்டர் அஸ்லம்...
            </div>
          )}
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-6 h-6 rounded bg-[#FF3300]/20 border border-[#FF3300]/30 flex items-center justify-center flex-shrink-0 p-1">
                  <img
                    src="https://img.icons8.com/ios-filled/100/FF3300/dragon.png"
                    alt="Dragon"
                    className="w-full h-full object-contain"
                    referrerPolicy="no-referrer"
                  />
                </div>
              )}
              <div className={`
                max-w-[80%] p-2 rounded border relative group whitespace-pre-wrap
                ${msg.role === 'user'
                  ? 'bg-[#00FFFF]/10 border-[#00FFFF]/30 text-[#00FFFF]'
                  : 'bg-[#111] border-[#222] text-[#888]'}
              `}>
                {msg.text}
                {msg.role === 'assistant' && (
                  <button
                    onClick={() => speakMessage(msg.text, i)}
                    className="absolute -right-8 top-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity text-[#FF3300] hover:scale-110"
                  >
                    {isSpeaking === i ? <VolumeX className="w-4 h-4 animate-pulse" /> : <Volume2 className="w-4 h-4" />}
                  </button>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-6 h-6 rounded bg-[#00FFFF]/20 border border-[#00FFFF]/30 flex items-center justify-center flex-shrink-0">
                  <User className="w-3 h-3 text-[#00FFFF]" />
                </div>
              )}
            </motion.div>
          ))}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3 justify-start"
            >
              <div className="w-6 h-6 rounded bg-[#FF3300]/20 border border-[#FF3300]/30 flex items-center justify-center flex-shrink-0 p-1">
                <img
                  src="https://img.icons8.com/ios-filled/100/FF3300/dragon.png"
                  alt="Dragon"
                  className="w-full h-full object-contain animate-pulse"
                  referrerPolicy="no-referrer"
                />
              </div>
              <div className="max-w-[80%] p-2 rounded border bg-[#111] border-[#222] text-[#444] animate-pulse">
                GROQ GPT-OSS-120B THINKING...
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="flex gap-2 z-10">
        <button
          onClick={clearMemory}
          title="Purge Memory"
          className="p-2 bg-black border border-[#222] rounded text-[#444] hover:text-[#FF3300] hover:border-[#FF3300] transition-all"
        >
          <Trash2 className="w-5 h-5" />
        </button>
        <button
          onClick={toggleListening}
          className={`
            p-2 rounded border transition-all
            ${isListening
              ? 'bg-[#FF3300]/20 border-[#FF3300] text-[#FF3300] shadow-[0_0_15px_rgba(255,51,0,0.3)]'
              : 'bg-[#111] border-[#222] text-[#888] hover:border-[#FF3300] hover:text-[#FF3300]'}
          `}
        >
          {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(inputText)}
          placeholder="கட்டளையை உள்ளிடவும்..."
          className="flex-1 bg-black border border-[#222] rounded px-3 py-2 text-[11px] font-mono focus:outline-none focus:border-[#00FFFF] transition-colors"
        />
        <button
          onClick={() => handleSendMessage(inputText)}
          className="p-2 bg-[#00FFFF]/10 border border-[#00FFFF]/30 rounded text-[#00FFFF] hover:bg-[#00FFFF]/20 transition-all"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
