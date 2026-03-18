import React from 'react';

type Props = {
  text: string;
};

export function MarkdownView({ text }: Props) {
  return (
    <div className="whitespace-pre-wrap break-words font-mono text-sm">
      {text}
    </div>
  );
}
