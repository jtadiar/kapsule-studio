
import React, { useState } from 'react';
import { Card } from './Card';
import { ClipboardIcon } from './icons/ClipboardIcon';
import { CheckIcon } from './icons/CheckIcon';

interface PromptPreviewProps {
  generatedPrompt: string;
}

export const PromptPreview: React.FC<PromptPreviewProps> = ({ generatedPrompt }) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = () => {
    if (!generatedPrompt) return;
    navigator.clipboard.writeText(generatedPrompt);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <Card title="3. Prompt Output">
      <div className="relative">
        <textarea
          readOnly
          value={generatedPrompt || 'Your generated prompt will appear here...'}
          className="w-full h-40 bg-gray-800 border border-gray-700 rounded-lg p-3 text-gray-300 resize-none text-sm leading-relaxed focus:ring-0 focus:border-gray-700"
        />
        <button
          onClick={handleCopy}
          disabled={!generatedPrompt}
          className="absolute top-3 right-3 p-2 bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-colors"
          aria-label="Copy prompt"
        >
          {isCopied ? (
            <CheckIcon className="w-5 h-5 text-green-400" />
          ) : (
            <ClipboardIcon className="w-5 h-5 text-gray-300" />
          )}
        </button>
      </div>
    </Card>
  );
};
