import React, { useState, useEffect } from 'react';
import { Card } from './Card';

interface VideoPreviewProps {
  isProcessing: boolean;
  videoUrl: string | null;
  errorMessage: string | null;
}

const PROCESSING_MESSAGES = [
  "Analyzing your inputs...",
  "Cooking up some sauce...",
  "Bringing your idea to life...",
  "Crafting cinematic magic...",
  "Syncing visuals to your beat...",
  "Generating your masterpiece..."
];

export const VideoPreview: React.FC<VideoPreviewProps> = ({ isProcessing, videoUrl, errorMessage }) => {
  const [messageIndex, setMessageIndex] = useState(0);

  // Rotate through processing messages
  useEffect(() => {
    if (!isProcessing) {
      setMessageIndex(0); // Reset when not processing
      return;
    }

    const interval = setInterval(() => {
      setMessageIndex((prevIndex) => (prevIndex + 1) % PROCESSING_MESSAGES.length);
    }, 3000); // Change message every 3 seconds

    return () => clearInterval(interval);
  }, [isProcessing]);

  const handleDownload = () => {
    if (videoUrl) {
      // Open video URL in new tab for download
      window.open(videoUrl, '_blank');
    }
  };

  return (
    <Card title="3. Preview & Download">
      <div className="aspect-[9/16] bg-gray-200 rounded-lg mb-4 flex items-center justify-center overflow-hidden max-w-md mx-auto">
        {isProcessing ? (
          <div className="w-full h-full bg-gray-100 flex flex-col items-center justify-center px-4">
            <div className="w-10 h-10 border-4 border-t-[#FF383A] border-gray-300 rounded-full animate-spin mb-4"></div>
            <p className="text-gray-700 font-medium text-center transition-all duration-500">
              {PROCESSING_MESSAGES[messageIndex]}
            </p>
            <p className="text-xs text-gray-500 mt-3">This may take 2-5 minutes</p>
          </div>
        ) : errorMessage ? (
          <div className="w-full h-full bg-red-50 flex flex-col items-center justify-center p-4">
            <p className="text-red-600 font-medium mb-2">❌ Error</p>
            <p className="text-sm text-red-500 text-center">{errorMessage}</p>
          </div>
        ) : videoUrl ? (
          <video 
            src={videoUrl}
            controls
            className="w-full h-full object-cover"
          >
            Your browser does not support the video tag.
          </video>
        ) : (
          <img 
            src="https://picsum.photos/seed/kapsule/506/900"
            alt="Video placeholder"
            className="w-full h-full object-cover"
          />
        )}
      </div>
      <button
        onClick={handleDownload}
        disabled={!videoUrl}
        className="w-full bg-[#FF383A] text-white font-bold py-2.5 px-4 rounded-lg transition-all duration-300 hover:bg-opacity-90 hover:scale-105 disabled:bg-gray-400 disabled:opacity-70 disabled:cursor-not-allowed disabled:scale-100"
      >
        {videoUrl ? 'Download Video' : 'Video Not Ready'}
      </button>
      {!videoUrl && !isProcessing && !errorMessage && (
        <p className="text-xs text-center text-gray-500 mt-2">Upload audio and generate a video to see results here.</p>
      )}
    </Card>
  );
};