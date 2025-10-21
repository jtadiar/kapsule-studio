import React, { useState } from 'react';
import { Card } from './Card';
import type { PromptOptions } from '../types';
import { GENRES, VISUAL_STYLES, CAMERA_MOVEMENTS, CAMERA_MOVEMENTS_VISUAL, MOODS, SUBJECTS, SETTINGS, DURATIONS, LIGHTING_STYLES, CAMERA_TYPES, CREATIVE_INTENSITIES, VISUAL_SUBJECTS } from '../constants';

interface PromptFormProps {
  promptOptions: PromptOptions;
  setPromptOptions: (options: PromptOptions) => void;
  onGenerate: () => void;
  isDisabled: boolean;
  onUsePreview: (text: string) => void;
}

const SelectInput: React.FC<{label: string, name: keyof PromptOptions, value: string, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void, options: string[]}> = ({label, name, value, onChange, options}) => (
    <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-600 mb-1">{label}</label>
        <select
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            className="w-full bg-[#FFFFFF] border border-[#C3C3C3] rounded-lg py-2 px-3 text-[#474747] focus:ring-2 focus:ring-[#FF383A] focus:border-[#FF383A] transition"
        >
            {options.map(option => <option key={option} value={option}>{option}</option>)}
        </select>
    </div>
);


export const PromptForm: React.FC<PromptFormProps> = ({ promptOptions, setPromptOptions, onGenerate, isDisabled, onUsePreview }) => {
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewText, setPreviewText] = useState<string>('');
  const [previewSource, setPreviewSource] = useState<'gemini' | 'rule_fallback' | null>(null);
  const [showCreativeNotes, setShowCreativeNotes] = useState(false);
  const [isReEnhancing, setIsReEnhancing] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLTextAreaElement>) => {
    setPromptOptions({
      ...promptOptions,
      [e.target.name]: e.target.value,
    });
  };

  // Detect if visual-only mode and provide appropriate camera options
  const isVisualOnly = VISUAL_SUBJECTS.includes(promptOptions.subject);
  const cameraOptions = isVisualOnly ? CAMERA_MOVEMENTS_VISUAL : CAMERA_MOVEMENTS;

  const handleRandomize = () => {
    // Helper to get random item from array
    const random = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
    
    // Randomly select subject first to determine camera options
    const randomSubject = random(SUBJECTS);
    const isVisualSubject = VISUAL_SUBJECTS.includes(randomSubject);
    const cameraMovementOptions = isVisualSubject ? CAMERA_MOVEMENTS_VISUAL : CAMERA_MOVEMENTS;
    
    setPromptOptions({
      genre: random(GENRES),
      visualStyle: random(VISUAL_STYLES),
      cameraMovement: random(cameraMovementOptions),
      mood: random(MOODS),
      subject: randomSubject,
      setting: random(SETTINGS),
      lighting: random(LIGHTING_STYLES),
      cameraType: random(CAMERA_TYPES),
      duration: random(DURATIONS),
      creativeIntensity: random(CREATIVE_INTENSITIES),
      extra: '', // Keep extra empty on randomize
    });
  };

  const handlePreview = async () => {
    setIsPreviewing(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const body = {
        genre: promptOptions.genre,
        visualStyle: promptOptions.visualStyle,
        cameraMovement: promptOptions.cameraMovement,
        mood: promptOptions.mood,
        subject: promptOptions.subject,
        setting: promptOptions.setting,
        lighting: promptOptions.lighting,
        cameraType: promptOptions.cameraType,
        duration: promptOptions.duration,
        creativeIntensity: promptOptions.creativeIntensity,
        extra: promptOptions.extra,
      };
      const res = await fetch(`${API_URL}/api/prompt/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error('Failed to load preview');
      const data = await res.json();
      setPreviewText(data.enhanced_prompt || '');
      setPreviewSource(data.source || null);
      setShowPreview(true);
    } catch (err) {
      setPreviewText(`Failed to load preview: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setPreviewSource(null);
      setShowPreview(true);
    } finally {
      setIsPreviewing(false);
    }
  };

  const handleUsePreview = () => {
    onUsePreview(previewText);
    setShowPreview(false);
  };

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(previewText);
  };

  const handleEnhanceWithGemini = async () => {
    setIsReEnhancing(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Send request with force_gemini flag
      const body = {
        genre: promptOptions.genre,
        visualStyle: promptOptions.visualStyle,
        cameraMovement: promptOptions.cameraMovement,
        mood: promptOptions.mood,
        subject: promptOptions.subject,
        setting: promptOptions.setting,
        lighting: promptOptions.lighting,
        cameraType: promptOptions.cameraType,
        duration: promptOptions.duration,
        creativeIntensity: promptOptions.creativeIntensity,
        extra: promptOptions.extra,
        force_gemini: true, // Force Gemini enhancement
      };
      
      const res = await fetch(`${API_URL}/api/prompt/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      
      if (!res.ok) throw new Error('Failed to enhance with Gemini');
      const data = await res.json();
      setPreviewText(data.enhanced_prompt || '');
      setPreviewSource('gemini');
    } catch (err) {
      alert(`Gemini enhancement failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsReEnhancing(false);
    }
  };

  return (
    <Card 
      title={
        <div className="flex items-center justify-between w-full">
          <span>2. Customize Your Video</span>
          <button
            onClick={handleRandomize}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-all hover:scale-105 text-sm font-medium"
            title="Randomize all options"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Randomize
          </button>
        </div>
      }
    >
        <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <SelectInput label="Genre" name="genre" value={promptOptions.genre} onChange={handleChange} options={GENRES} />
                <SelectInput label="Visual Style" name="visualStyle" value={promptOptions.visualStyle} onChange={handleChange} options={VISUAL_STYLES} />
                <SelectInput label="Subject" name="subject" value={promptOptions.subject} onChange={handleChange} options={SUBJECTS} />
                <SelectInput label="Setting" name="setting" value={promptOptions.setting} onChange={handleChange} options={SETTINGS} />
                <SelectInput label="Camera Movement" name="cameraMovement" value={promptOptions.cameraMovement} onChange={handleChange} options={cameraOptions} />
                <SelectInput label="Mood" name="mood" value={promptOptions.mood} onChange={handleChange} options={MOODS} />
                <SelectInput label="Lighting Style" name="lighting" value={promptOptions.lighting} onChange={handleChange} options={LIGHTING_STYLES} />
                <SelectInput label="Camera Type / Lens" name="cameraType" value={promptOptions.cameraType} onChange={handleChange} options={CAMERA_TYPES} />
            </div>
            <div className="grid grid-cols-2 gap-4">
                <SelectInput label="Creative Intensity" name="creativeIntensity" value={promptOptions.creativeIntensity} onChange={handleChange} options={CREATIVE_INTENSITIES} />
                <SelectInput label="Duration" name="duration" value={promptOptions.duration} onChange={handleChange} options={DURATIONS} />
            </div>
            
            {/* Expandable Creative Notes Section */}
            <div>
                <button
                    type="button"
                    onClick={() => setShowCreativeNotes(!showCreativeNotes)}
                    className="w-full flex items-center justify-between py-2 px-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left"
                >
                    <span className="text-sm font-medium text-gray-700">
                        Creative Notes (Optional)
                    </span>
                    <svg 
                        className={`w-5 h-5 text-gray-600 transition-transform ${showCreativeNotes ? 'rotate-180' : ''}`} 
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>
                
                {showCreativeNotes && (
                    <div className="mt-2 space-y-1">
                        <textarea
                            id="extra"
                            name="extra"
                            value={promptOptions.extra}
                            onChange={handleChange}
                            rows={3}
                            placeholder="Describe story elements, colors, or effects — e.g. 'mirror transitions,' 'flashes of red light,' or 'liquid morphing visuals.'"
                            className="w-full bg-[#FFFFFF] border border-[#C3C3C3] rounded-lg py-2 px-3 text-[#474747] focus:ring-2 focus:ring-[#FF383A] focus:border-[#FF383A] transition"
                        />
                    </div>
                )}
            </div>
            <button
                onClick={handlePreview}
                disabled={isDisabled || isPreviewing}
                className="w-full bg-white border-2 border-[#FF383A] text-[#FF383A] font-bold py-2.5 px-4 rounded-lg transition-all duration-300 hover:bg-[#FFF5F5] hover:scale-105 disabled:bg-gray-100 disabled:border-gray-400 disabled:text-gray-400 disabled:opacity-70 disabled:cursor-not-allowed disabled:scale-100"
            >
                {isPreviewing ? 'Generating Preview…' : '🔍 Preview Enhanced Prompt'}
            </button>
            <button
                onClick={onGenerate}
                disabled={isDisabled}
                className="w-full bg-[#FF383A] text-white font-bold py-2.5 px-4 rounded-lg transition-all duration-300 hover:bg-opacity-90 hover:scale-105 disabled:bg-gray-400 disabled:opacity-70 disabled:cursor-not-allowed disabled:scale-100"
            >
                Generate Video
            </button>
        </div>

        {/* Preview Modal */}
        {showPreview && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setShowPreview(false)}>
            <div className="w-full max-w-3xl bg-white rounded-xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800">Enhanced Prompt</h3>
                {previewSource && (
                  <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                    previewSource === 'gemini' 
                      ? 'bg-purple-100 text-purple-700' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {previewSource === 'gemini' ? '✨ Gemini Enhanced' : '🔧 Rule-Based'}
                  </span>
                )}
              </div>
              
              <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
                <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{previewText}</p>
              </div>
              
              <div className="flex flex-col gap-3">
                {/* Gemini Enhancement Button - Only show if not already Gemini enhanced */}
                {previewSource !== 'gemini' && (
                  <button
                    onClick={handleEnhanceWithGemini}
                    disabled={isReEnhancing}
                    className="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white font-bold py-2.5 px-4 rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                  >
                    {isReEnhancing ? '✨ Enhancing with Gemini...' : '✨ Enhance with Gemini 2.5'}
                  </button>
                )}
                
                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={handleCopyToClipboard}
                    className="flex-1 bg-gray-100 text-gray-700 font-semibold py-2.5 px-4 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    📋 Copy
                  </button>
                  <button
                    onClick={handleUsePreview}
                    className="flex-1 bg-[#FF383A] text-white font-bold py-2.5 px-4 rounded-lg hover:bg-opacity-90 transition-all"
                  >
                    ✅ Use This Prompt
                  </button>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="flex-1 bg-gray-700 text-white font-semibold py-2.5 px-4 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
    </Card>
  );
};