import React from 'react';
import { MarkdownView } from './MarkdownView';

type ChatRole = 'user' | 'assistant';

type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
  createdAt: string;
};

type Props = {
  chatHistory: ChatMessage[];
  liveReply: string;
  loading: boolean;
  isTyping: boolean;
  chatContainerRef: React.RefObject<HTMLDivElement | null>;
};

export function ChatFeed({
  chatHistory,
  liveReply,
  loading,
  isTyping,
  chatContainerRef,
}: Props) {
  return (
    <div
      ref={chatContainerRef}
      className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide"
    >
      {chatHistory.map((item) => (
        <div
          key={item.id}
          className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[85%] p-4 border rounded-2xl ${
              item.role === 'user'
                ? 'border-green-500/40 bg-green-500/5 text-green-100'
                : 'border-blue-500/30 bg-blue-500/5 text-blue-100'
            }`}
          >
            <div className="text-[8px] opacity-50 mb-1 tracking-tighter">
              {item.role.toUpperCase()}
            </div>
            <MarkdownView text={item.text} />
          </div>
        </div>
      ))}

      {(liveReply || loading) && (
        <div className="flex justify-start">
          <div className="max-w-[85%] p-4 border border-pink-500/40 bg-pink-500/5 text-pink-100 rounded-2xl">
            <MarkdownView text={liveReply || 'Analyzing...'} />
            {isTyping && (
              <span className="inline-block w-2 h-4 bg-pink-500 ml-1 animate-pulse" />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
