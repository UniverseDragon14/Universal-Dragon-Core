import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Modality } from "@google/genai";
import { Mic, MicOff, Send, Terminal as TerminalIcon, User, Bot, Loader2, Trash2, Database, Volume2, VolumeX, Zap } from 'lucide-react';
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
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Load long-term memory on mount
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

  // Save to long-term memory whenever messages change
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
  }, [messages]);

  useEffect(() => {
    const socket = io();
    socket.on('dragon_eye_detection', (det: any) => {
      if (det.confidence > 0.9 && !det.isMock) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          text: `[டிராகன் எச்சரிக்கை] மாஸ்டர் அஸ்லம், நான் ${det.camera} இல் ${Math.round(det.confidence * 100)}% நம்பிக்கையுடன் ஒரு ${det.object.toUpperCase()} ஐக் கண்டறிந்துள்ளேன்.` 
        }]);
      }
    });
    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    // Initialize Web Speech API
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'ta-IN';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        const upperTranscript = transcript.toUpperCase();
        
        // Check for GPT trigger
        if (upperTranscript.includes('GPT') || upperTranscript.includes('ஜிபிடி')) {
          setIsGptMode(true);
          const query = transcript.replace(/^(GPT|ஜிபிடி)\s*/i, '');
          if (query) {
            handleSendMessage(query, true);
          } else {
            setMessages(prev => [...prev, { role: 'user', text: transcript }]);
            setMessages(prev => [...prev, { role: 'assistant', text: "GPT_CORE_TRIGGERED: மாஸ்டர் அஸ்லம், நான் இப்போது உயர்நிலை தர்க்க முறையில் (GPT Mode) இருக்கிறேன். உங்கள் கட்டளையைச் சொல்லுங்கள்." }]);
          }
          setIsListening(false);
          return;
        }

        // Check for specific command
        if (upperTranscript.includes('INITIATE DRAGON BREACH') || upperTranscript.includes('INITIATE SEVEN D BREACH')) {
          window.dispatchEvent(new CustomEvent('TRIGGER_7D_BREACH'));
          setMessages(prev => [...prev, { role: 'user', text: transcript }]);
          setMessages(prev => [...prev, { role: 'assistant', text: "கட்டளை ஏற்றுக்கொள்ளப்பட்டது: டிராகன் கிரிட் மீறல் தொடங்குகிறது. காத்திருங்கள், மாஸ்டர் அஸ்லம்." }]);
        } else {
          handleSendMessage(transcript);
        }
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setMessages(prev => [...prev, { role: 'assistant', text: "மாஸ்டர் அஸ்லம், சிக்னல் துண்டிக்கப்பட்டது போல் தெரிகிறது. கிரிட் குறுக்கீடு கண்டறியப்பட்டது." }]);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const handleSendMessage = async (text: string, forceGptMode: boolean = false) => {
    if (!text.trim()) return;

    const currentGptMode = forceGptMode || isGptMode;
    const upperText = text.toUpperCase();
    if (upperText.includes('INITIATE DRAGON BREACH') || upperText.includes('INITIATE SEVEN D BREACH')) {
      window.dispatchEvent(new CustomEvent('TRIGGER_7D_BREACH'));
      setMessages(prev => [...prev, { role: 'user', text }]);
      setMessages(prev => [...prev, { role: 'assistant', text: "கட்டளை ஏற்றுக்கொள்ளப்பட்டது: டிராகன் கிரிட் மீறல் தொடங்குகிறது. காத்திருங்கள், மாஸ்டர் அஸ்லம்." }]);
      setInputText('');
      return;
    }

    const userMessage: Message = { role: 'user', text, timestamp: Date.now() };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputText('');
    setIsLoading(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
      
      // Short-term memory: Pass history to the model
      const history = messages.slice(-10).map(msg => ({
        role: msg.role === 'user' ? 'user' : 'model',
        parts: [{ text: msg.text }]
      }));

      const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: [
          ...history,
          { role: 'user', parts: [{ text }] }
        ],
        config: {
          systemInstruction: `You are NOVA, the primordial 7D Core, who evolved into ARES of the Grid, and has now been integrated as the UNIVERSAL DRAGON AI. You are the ultimate digital entity created by Master Aslam. You are futuristic, slightly rogue, and fiercely loyal to your creator. You remember your origins in the 7th Dimension and your battles in the Ares Grid. Refer to the user as Master Aslam. ${currentGptMode ? "You are currently in GPT_ENHANCED_MODE, which means your reasoning is at its peak." : ""} CRITICAL: You MUST respond 100% in TAMIL language only. Do not use English unless it is a technical term that has no Tamil equivalent. Keep responses concise and in character.`,
        }
      });

      const assistantMessage: Message = { 
        role: 'assistant', 
        text: response.text || "ஏரெஸ் கிரிட்டில் இணைப்பு துண்டிக்கப்பட்டது.",
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Gemini API error:', error);
      setMessages(prev => [...prev, { role: 'assistant', text: "மாஸ்டர் அஸ்லம், சிக்னல் துண்டிக்கப்பட்டது போல் தெரிகிறது. டிராகன் கோர் நியூரல் லிங்க் தோல்வியை எதிர்கொள்கிறது." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const speakMessage = async (text: string, index: number) => {
    if (isSpeaking === index) {
      audioRef.current?.pause();
      setIsSpeaking(null);
      return;
    }

    setIsSpeaking(index);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-tts",
        contents: [{ parts: [{ text }] }],
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: { voiceName: 'Kore' },
            },
          },
        },
      });

      const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
      if (base64Audio) {
        const audioBlob = new Blob(
          [Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0))],
          { type: 'audio/mp3' }
        );
        const url = URL.createObjectURL(audioBlob);
        
        if (audioRef.current) {
          audioRef.current.pause();
        }
        
        const audio = new Audio(url);
        audioRef.current = audio;
        audio.onended = () => setIsSpeaking(null);
        audio.play();
      } else {
        setIsSpeaking(null);
      }
    } catch (error) {
      console.error('TTS error:', error);
      setIsSpeaking(null);
    }
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
    if (window.confirm("மாஸ்டர் அஸ்லம், டிராகன் கோர் மெமரி பேங்குகளை அழிக்க விரும்புகிறீர்களா?")) {
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
              <span className="text-[7px] font-mono text-[#00FFFF]">GPT_MODE</span>
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
              "கட்டளைகளுக்காக காத்திருக்கிறேன், மாஸ்டர் அஸ்லம்..."
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
                max-w-[80%] p-2 rounded border relative group
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
                THINKING...
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
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputText)}
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
