import React, { useState, useEffect, useCallback } from 'react';
import { UploadSection } from './components/UploadSection';
import { PromptForm } from './components/PromptForm';
import { VideoPreview } from './components/VideoPreview';
import type { PromptOptions } from './types';
import { DURATIONS, GENRES, VISUAL_STYLES, CAMERA_MOVEMENTS, CAMERA_MOVEMENTS_VISUAL, MOODS, SUBJECTS, SETTINGS, LIGHTING_STYLES, CAMERA_TYPES, CREATIVE_INTENSITIES, VISUAL_SUBJECTS } from './constants';

const App: React.FC = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  
  const [promptOptions, setPromptOptions] = useState<PromptOptions>({
    genre: GENRES[0],
    visualStyle: VISUAL_STYLES[0],
    cameraMovement: CAMERA_MOVEMENTS_VISUAL[0], // Start with visual camera for "None (Visual Only)"
    mood: MOODS[0],
    subject: SUBJECTS[0],        // "None (Visual Only)"
    setting: SETTINGS[0],        // "Color Studio Background"
    lighting: LIGHTING_STYLES[0], // "Natural Sunlight"
    cameraType: CAMERA_TYPES[0],  // "50mm Prime"
    duration: DURATIONS[0],
    creativeIntensity: CREATIVE_INTENSITIES[0], // "Balanced"
    extra: '',
  });

  const [isVideoProcessing, setIsVideoProcessing] = useState<boolean>(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [customPrompt, setCustomPrompt] = useState<string | null>(null);

  // Poll for job status
  useEffect(() => {
    if (!jobId || !isVideoProcessing) return;

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    let pollInterval: number;

    const pollJobStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/result/${jobId}`);
        
        if (!response.ok) {
          throw new Error('Failed to get job status');
        }

        const data = await response.json();

        if (data.status === 'complete') {
          setVideoUrl(data.video_url);
          setIsVideoProcessing(false);
          clearInterval(pollInterval);
        } else if (data.status === 'error') {
          setErrorMessage(data.error || 'Video generation failed');
          setIsVideoProcessing(false);
          clearInterval(pollInterval);
        }
        // Continue polling if status is 'queued' or 'processing'
      } catch (error) {
        console.error('Polling error:', error);
        setErrorMessage('Failed to check job status');
        setIsVideoProcessing(false);
        clearInterval(pollInterval);
      }
    };

    // Start polling every 3 seconds
    pollInterval = window.setInterval(pollJobStatus, 3000);
    pollJobStatus(); // Call immediately

    return () => clearInterval(pollInterval);
  }, [jobId, isVideoProcessing]);

  // Reset camera movement when switching between visual/performance modes
  useEffect(() => {
    const isVisualOnly = VISUAL_SUBJECTS.includes(promptOptions.subject);
    const currentCameraValid = isVisualOnly 
      ? CAMERA_MOVEMENTS_VISUAL.includes(promptOptions.cameraMovement)
      : CAMERA_MOVEMENTS.includes(promptOptions.cameraMovement);
    
    if (!currentCameraValid) {
      setPromptOptions(prev => ({
        ...prev,
        cameraMovement: isVisualOnly ? CAMERA_MOVEMENTS_VISUAL[0] : CAMERA_MOVEMENTS[0]
      }));
    }
  }, [promptOptions.subject]);

  const handleGenerateClick = async () => {
    const options = promptOptions;
    if (!areAllOptionsSelected || !audioUrl) return;

    console.log("Sending structured options to backend for prompt enhancement");

    try {
      setIsVideoProcessing(true);
      setVideoUrl(null);
      setErrorMessage(null);

      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const requestBody: any = {
        ...options,
        audio_url: audioUrl,
      };
      
      // If user has selected a custom prompt, include it
      if (customPrompt) {
        requestBody.prompt = customPrompt;
        console.log("Using custom prompt from preview");
      } else {
        console.log("Backend will build enhanced prompt from options");
      }
      
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Generation failed');
      }

      const data = await response.json();
      setJobId(data.job_id);
      console.log("Job created:", data.job_id);
    } catch (error) {
      setIsVideoProcessing(false);
      console.error('Generation error:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Unknown error');
    }
  };

  const handleUsePreview = (previewText: string) => {
    setCustomPrompt(previewText);
    console.log("Custom prompt set, will be used for next generation");
  };

  const areAllOptionsSelected = Object.values(promptOptions).every(val => typeof val === 'string' && (val.length > 0 || val === promptOptions.extra));


  return (
    <div className="min-h-screen bg-[#F7F7F7] text-gray-800 p-4 sm:p-8">
      <main className="max-w-7xl mx-auto">
        <header className="flex justify-center mb-12">
          <img 
            src="/Vector.png" 
            alt="Kapsule Studio" 
            className="h-10 sm:h-12 object-contain"
          />
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="lg:col-span-1 flex flex-col gap-8">
            <UploadSection 
              uploadedFile={uploadedFile} 
              setUploadedFile={setUploadedFile} 
              setAudioUrl={setAudioUrl}
            />
            <PromptForm 
              promptOptions={promptOptions}
              setPromptOptions={setPromptOptions}
              onGenerate={handleGenerateClick}
              isDisabled={!areAllOptionsSelected || !audioUrl}
              onUsePreview={handleUsePreview}
            />
          </div>
          <div className="lg:col-span-1 flex flex-col">
            <VideoPreview 
              isProcessing={isVideoProcessing} 
              videoUrl={videoUrl}
              errorMessage={errorMessage}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;