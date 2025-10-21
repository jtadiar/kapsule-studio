import type { PromptOptions } from './types';

/**
 * Frontend Prompt Enhancer
 * 
 * NOTE: This is a reference implementation that matches the backend.
 * The actual prompt enhancement happens on the backend API.
 * This file can be used for client-side preview or offline testing.
 */

const genreDescriptors: Record<string, string> = {
  "Pop": "vibrant, saturated colors, clean visuals, high-energy editing, slick choreography, polished look",
  "Hip Hop": "urban landscapes, cinematic street style, dynamic camera angles, raw energy, story-driven visuals",
  "EDM": "pulsating strobe lights, neon trails, abstract geometric patterns, visuals synced to the beat, futuristic aesthetic",
  "Rock": "high-contrast lighting, raw performance energy, gritty textures, dynamic band shots, lens flares",
  "Lo-Fi": "dreamy, nostalgic visuals, grainy 16mm film texture, soft focus, warm analog tones, lens imperfections",
  "House": "stylish club atmosphere, vibrant dancefloor scenes, hypnotic repeating visuals, energetic dancers, seamless transitions",
  "R&B": "moody, atmospheric lighting, intimate close-ups, smooth and soulful camera movements, luxurious textures",
  "Trap": "dark, gritty urban environment, slow-motion sequences, intense close-ups, atmospheric smoke, neon-lit nights",
};

const styleDescriptors: Record<string, string> = {
  "Cinematic": "shot on anamorphic lenses, shallow depth of field, professional color grading, filmic motion blur, epic wide shots",
  "Anime": "vibrant cel-shaded animation, dynamic action lines, expressive character designs, detailed backgrounds, dramatic perspectives",
  "2D Illustration": "fluid hand-drawn animation, textured paper backgrounds, minimalist color palette, charming character movements",
  "Trippy": "kaleidoscopic effects, liquid light show, surreal transformations, datamoshing, flowing psychedelic patterns, reality-bending visuals",
  "Realistic CGI": "photorealistic rendering, hyper-detailed textures, seamless VFX integration, lifelike character animation, physically-based lighting",
  "Grunge": "shaky handheld camera, distressed 90s film look, high contrast black and white, lens dirt, underexposed scenes, raw and unfiltered feel",
  "Vintage": "Super 8 film grain, faded color palette, light leaks, nostalgic and retro aesthetic, classic film aspect ratio",
};

const cameraDescriptors: Record<string, string> = {
    "Slow Pan": "a deliberate, sweeping slow pan, revealing the scene with a sense of grandeur",
    "Orbit": "a smooth 360-degree orbit shot around the subject, creating a dramatic and focal point",
    "Dolly In": "a slow dolly-in, gradually moving closer to the subject to build tension or intimacy",
    "Static": "a carefully composed static shot, using the framing to tell a story like a living photograph",
    "Handheld": "raw, intimate handheld camera work, capturing the energy with a sense of immediacy and realism",
    "Tracking": "a precise tracking shot following the subject's movement, creating a dynamic and immersive experience",
};

const moodDescriptors: Record<string, string> = {
    "Energetic": "fast-paced editing, vibrant color flashes, dynamic motion, and a sense of exhilarating movement",
    "Melancholic": "soft, diffused lighting, slow-motion details, a muted and desaturated color palette, and a focus on introspection",
    "Uplifting": "bright, warm lighting, sweeping camera shots, saturated, optimistic colors, and a feeling of hope and positivity",
    "Dark": "low-key lighting, deep shadows, a high-contrast and gritty look, creating a sense of mystery and tension",
    "Moody": "atmospheric and evocative lighting, rich color tones, and a focus on emotion and feeling over narrative",
    "Euphoric": "dreamlike visuals, lens flares, glowing particles, slow-motion expressions of joy, and an overwhelming sense of bliss"
};

const subjectDescriptors: Record<string, string> = {
    "Solo Dancer": "an expressive solo dancer, focusing on fluid, powerful movements and intricate choreography",
    "Band Performing": "a full band performing with raw energy, capturing the interplay between musicians and the live intensity",
    "DJ": "a DJ in command of the decks, with visuals of the crowd, the lighting rig, and the energy of the event",
    "Singer": "an intimate and emotional focus on a singer's performance, capturing every nuance of their expression",
    "Musician in Studio": "a musician in a creative studio environment, surrounded by instruments and technology, capturing the process of creation",
    "Abstract Performer": "an abstract human form made of light, energy, or particles, moving and transforming with the music"
};

const settingDescriptors: Record<string, string> = {
    "Music Studio": "a high-tech music studio filled with glowing LED lights, vintage synthesizers, and reflective surfaces",
    "Stage Performance": "a massive concert stage with a spectacular light show, smoke machines, and an adoring crowd",
    "City Rooftop": "a sprawling city rooftop at night, with panoramic views of neon-lit skyscrapers and flying vehicles",
    "Desert": "a vast, surreal desert landscape at sunset, with stark silhouettes and an otherworldly color palette",
    "Club": "a pulsating, underground nightclub with immersive LED screens, a packed dancefloor, and a hazy, energetic atmosphere",
    "Abstract Space": "a non-physical, ever-shifting abstract dimension of light, color, and geometric shapes that reacts to the music"
};

export const buildEnhancedPrompt = (options: PromptOptions): string => {
  const { genre, visualStyle, cameraMovement, mood, subject, setting, duration, extra } = options;

  // Look up the detailed descriptors, falling back to the base option if not found
  const genreText = genreDescriptors[genre] || genre.toLowerCase();
  const styleText = styleDescriptors[visualStyle] || visualStyle.toLowerCase();
  const cameraText = cameraDescriptors[cameraMovement] || cameraMovement.toLowerCase();
  const moodText = moodDescriptors[mood] || mood.toLowerCase();
  const subjectText = subjectDescriptors[subject] || subject.toLowerCase();
  const settingText = settingDescriptors[setting] || setting.toLowerCase();
  
  // Build a more structured, descriptive prompt
  const corePrompt = `A music video for a ${genre} track. The scene is set in ${settingText}, featuring ${subjectText}.`;
  
  const visualDirection = `The visual style is ${visualStyle.toLowerCase()}, defined by ${styleText}. The mood is intensely ${mood.toLowerCase()}, conveyed through ${moodText}.`;
  
  const cinematography = `Cinematography is key, utilizing ${cameraText}. Incorporate professional cinematic lighting, high-end color grading.`;
  
  const extraDetails = extra.trim() ? `Additional creative direction: ${extra.trim()}.` : '';

  const finalInstructions = `The final ${duration} output must be a visually stunning, polished, and unique visual experience. Avoid phone screens, UI elements, text overlays, watermarks, or logos.`;

  const fullPrompt = [corePrompt, visualDirection, cinematography, extraDetails, finalInstructions]
    .filter(Boolean)
    .join(' ');

  return fullPrompt.replace(/\s\s+/g, ' ').trim();
};

