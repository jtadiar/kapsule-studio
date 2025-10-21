import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Card } from './Card';
import { UploadIcon } from './icons/UploadIcon';
import { CheckIcon } from './icons/CheckIcon';

interface UploadSectionProps {
  uploadedFile: File | null;
  setUploadedFile: (file: File | null) => void;
  setAudioUrl: (url: string | null) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({ uploadedFile, setUploadedFile, setAudioUrl }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Audio timeline state
  const [audioDuration, setAudioDuration] = useState(0);
  const [segmentStart, setSegmentStart] = useState(0);
  const [segmentEnd, setSegmentEnd] = useState(15);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [audioUrl, setLocalAudioUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);

  const loadAudioFile = (file: File) => {
    setUploadedFile(file);
    setUploadSuccess(false);
    setAudioUrl(null);
    setAudioError(null);
    
    // Create object URL for audio element
    const url = URL.createObjectURL(file);
    setLocalAudioUrl(url);
    
    // Load audio to get duration
    const audio = new Audio(url);
    audio.addEventListener('loadedmetadata', () => {
      const duration = audio.duration;
      setAudioDuration(duration);
      
      if (duration < 15) {
        setAudioError('Audio must be at least 15 seconds long');
        setSegmentStart(0);
        setSegmentEnd(duration);
      } else {
        setAudioError(null);
        setSegmentStart(0);
        setSegmentEnd(15);
      }
    });
    
    audio.addEventListener('error', () => {
      setAudioError('Failed to load audio file');
    });
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      loadAudioFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
  };

  const handleDrop = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
     if (file && (file.type === "audio/mpeg" || file.type === "audio/wav" || file.type === "audio/m4a")) {
        loadAudioFile(file);
    }
  };

  // Audio playback handlers
  const handlePlayPause = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.currentTime = segmentStart;
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  // Update current time during playback
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      const time = audio.currentTime;
      setCurrentTime(time);
      
      // Stop playback at segment end
      if (time >= segmentEnd) {
        audio.pause();
        audio.currentTime = segmentStart;
        setIsPlaying(false);
      }
    };

    const handlePause = () => {
      setIsPlaying(false);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('pause', handlePause);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('pause', handlePause);
    };
  }, [segmentEnd, segmentStart]);

  // Timeline marker drag handlers
  const handleMarkerMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    if (!isDragging || !timelineRef.current) return;

    const handleMouseMove = (e: MouseEvent) => {
      const timeline = timelineRef.current;
      if (!timeline) return;

      const rect = timeline.getBoundingClientRect();
      const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      const percentage = x / rect.width;
      const newStart = percentage * audioDuration;

      // Constrain to valid range
      const maxStart = audioDuration - 15;
      const constrainedStart = Math.max(0, Math.min(newStart, maxStart));
      
      setSegmentStart(constrainedStart);
      setSegmentEnd(constrainedStart + 15);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, audioDuration]);
  
  const handleUpload = async () => {
    if (!uploadedFile) return;
    setIsUploading(true);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Step 1: Request signed upload URL from backend
      const urlResponse = await fetch(`${API_URL}/api/upload-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: uploadedFile.name,
          content_type: uploadedFile.type,
          file_size: uploadedFile.size,
        }),
      });
      
      if (!urlResponse.ok) {
        const error = await urlResponse.json();
        throw new Error(error.detail || 'Failed to get upload URL');
      }
      
      const { upload_url, gcs_uri } = await urlResponse.json();
      
      // Step 2: Upload file directly to GCS using signed URL
      const uploadResponse = await fetch(upload_url, {
        method: 'PUT',
        headers: {
          'Content-Type': uploadedFile.type,
        },
        body: uploadedFile,
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Failed to upload file to storage');
      }
      
      // Step 3: Notify backend to process the uploaded file (extract segment if needed)
      const processResponse = await fetch(`${API_URL}/api/process-upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gcs_uri: gcs_uri,
          start_time: segmentStart,
          end_time: segmentEnd,
        }),
      });
      
      if (!processResponse.ok) {
        const error = await processResponse.json();
        throw new Error(error.detail || 'Failed to process upload');
      }
      
      const data = await processResponse.json();
      
      setIsUploading(false);
      setUploadSuccess(true);
      setAudioUrl(data.audio_url);
      
      // Stop playback on successful upload
      if (audioRef.current) {
        audioRef.current.pause();
        setIsPlaying(false);
      }
    } catch (error) {
      setIsUploading(false);
      console.error('Upload error:', error);
      alert(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };
  
  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card title="1. Upload Track">
      <div className="flex flex-col space-y-4">
        {/* Hidden audio element for playback */}
        {audioUrl && <audio ref={audioRef} src={audioUrl} />}
        
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".mp3,.wav,.m4a"
          className="hidden"
        />
        <label
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-[#C3C3C3] rounded-xl cursor-pointer hover:border-gray-400 hover:bg-gray-50 transition-colors duration-300"
        >
          <UploadIcon className="w-8 h-8 text-gray-500 mb-2" />
          <p className="text-gray-600">Drag & drop or click to upload</p>
          <p className="text-xs text-gray-500">.mp3, .wav, or .m4a</p>
        </label>
        
        {uploadedFile && (
          <div className="bg-gray-100 p-3 rounded-lg text-sm">
            <p className="font-medium text-gray-800 truncate">{uploadedFile.name}</p>
            <p className="text-gray-600">{formatBytes(uploadedFile.size)} - {uploadedFile.type}</p>
          </div>
        )}

        {/* Audio Error Message */}
        {audioError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-600 text-sm font-medium">{audioError}</p>
          </div>
        )}

        {/* Audio Timeline Section */}
        {uploadedFile && audioDuration > 0 && !audioError && (
          <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-700">Select 15-Second Segment</h3>
              <span className="text-xs text-gray-500">
                {formatTime(segmentStart)} - {formatTime(segmentEnd)} ({formatTime(segmentEnd - segmentStart)})
              </span>
            </div>

            {/* Play/Pause Button */}
            <div className="flex items-center space-x-4">
              <button
                onClick={handlePlayPause}
                className="w-12 h-12 rounded-full bg-[#FF383A] hover:bg-red-600 flex items-center justify-center transition-all shadow-md hover:shadow-lg"
                title={isPlaying ? "Pause" : "Play"}
              >
                {isPlaying ? (
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                )}
              </button>

              {/* Timeline */}
              <div className="flex-1">
                <div 
                  ref={timelineRef}
                  className="relative h-16 bg-gray-300 rounded-lg overflow-visible"
                >
                  {/* Draggable 15-second segment window */}
                  <div 
                    className="absolute h-full bg-[#FF383A] rounded-lg shadow-lg cursor-grab active:cursor-grabbing hover:bg-red-600 transition-colors z-20"
                    style={{
                      left: `${(segmentStart / audioDuration) * 100}%`,
                      width: `${(15 / audioDuration) * 100}%`
                    }}
                    onMouseDown={handleMarkerMouseDown}
                    title="Drag to reposition 15-second segment"
                  />
                  
                  {/* Playback position indicator - white line */}
                  {isPlaying && currentTime >= segmentStart && currentTime <= segmentEnd && (
                    <div 
                      className="absolute w-1 h-full bg-white shadow-lg z-30 rounded-full"
                      style={{
                        left: `${(currentTime / audioDuration) * 100}%`
                      }}
                    />
                  )}
                </div>
                
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Drag the red window to select 15 seconds • Total duration: {formatTime(audioDuration)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Upload Button with Success State */}
        <button
          onClick={handleUpload}
          disabled={!uploadedFile || isUploading || uploadSuccess || !!audioError || audioDuration < 15}
          className={`w-full font-bold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center space-x-2 ${
            uploadSuccess 
              ? 'bg-green-500 text-white cursor-not-allowed' 
              : 'bg-[#FF383A] text-white hover:bg-opacity-90 hover:scale-105 disabled:bg-gray-400 disabled:opacity-70 disabled:cursor-not-allowed disabled:scale-100'
          }`}
        >
          {uploadSuccess && <CheckIcon className="w-5 h-5" />}
          <span>
            {isUploading ? 'Uploading...' : uploadSuccess ? 'Track Uploaded' : 'Upload Selected Segment'}
          </span>
        </button>
      </div>
    </Card>
  );
};