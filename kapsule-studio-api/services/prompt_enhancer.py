"""
Prompt Enhancement Service for Veo Video Generation

Transforms structured options into detailed, cinematic prompts optimized for Veo 3.0.
Supports both human performance and abstract visual-only modes.
Enhanced with music video quality enforcement and style-specific controls.
"""

import logging

logger = logging.getLogger(__name__)

# Genre descriptors
GENRE_DESCRIPTORS = {
    "Pop": "vibrant, saturated colors, clean visuals, high-energy editing, slick choreography, polished look",
    "Hip Hop": "urban landscapes, cinematic street style, dynamic camera angles, raw energy, story-driven visuals",
    "EDM": "pulsating strobe lights, neon trails, abstract geometric patterns, visuals synced to the beat, futuristic aesthetic",
    "Rock": "high-contrast lighting, raw performance energy, gritty textures, dynamic band shots, lens flares",
    "Lo-Fi": "dreamy, nostalgic visuals, grainy 16mm film texture, soft focus, warm analog tones, lens imperfections",
    "House": "stylish club atmosphere, vibrant dancefloor scenes, hypnotic repeating visuals, energetic dancers, seamless transitions",
    "R&B": "moody, atmospheric lighting, intimate close-ups, smooth and soulful camera movements, luxurious textures",
    "Trap": "dark, gritty urban environment, slow-motion sequences, intense close-ups, atmospheric smoke, neon-lit nights",
}

# Visual style descriptors - STRENGTHENED with medium-specific language
STYLE_DESCRIPTORS = {
    "Cinematic": "shot on professional cinema cameras with anamorphic lenses, shallow depth of field, filmic motion blur, epic composition, theatrical color grading",
    
    "Anime": "RENDERED AS ANIME ANIMATION with vibrant cel-shaded style, bold line work, expressive character designs, dynamic action sequences, stylized backgrounds, NOT photorealistic",
    
    "2D Illustration": "CREATED AS 2D HAND-DRAWN ANIMATION with illustrative style, textured brush strokes, flat color planes, artistic character design, NOT live-action, NOT photorealistic",
    
    "Trippy": "psychedelic visual effects with kaleidoscopic patterns, liquid light distortions, surreal transformations, reality-bending warps, abstract flowing visuals",
    
    "Realistic CGI": "high-end 3D CGI render with photorealistic textures, advanced ray tracing, seamless VFX integration, physically-based materials and lighting",
    
    "Grunge": "raw underground aesthetic with shaky handheld camera, distressed film look, high contrast grain, lens dirt, underexposed moody atmosphere",
    
    "Vintage": "authentic retro film aesthetic with Super 8 grain, faded color palette, natural light leaks, nostalgic warm tones, vintage aspect ratio"
}

# Camera movement descriptors for performance mode - ENHANCED with angle variety
CAMERA_DESCRIPTORS = {
    # HIGH-ENERGY EDITING OPTIONS
    "Dynamic Multi-Angle Cuts": "rapid cuts between multiple camera angles (wide establishing, medium action, tight details, overhead shots) changing every 1-2 seconds, creating energetic pacing with varied perspectives",
    "Beat-Matched Cuts": "quick transitions synchronized to the track's beat, cutting between complementary angles (side, three-quarter, low angle, detail shots) with rhythmic precision",
    "Rapid Transitions": "fast whip pans, snap zooms, and energetic reframes between angles, creating kinetic momentum and explosive visual pacing",
    "Multi-Angle Coverage": "dynamic multi-camera edit, switching between establishing, mid, and close angles like a live performance",

    # CONTINUOUS MOTION OPTIONS (aliases maintained for backward compatibility)
    "Smooth Tracking Shot": "a fluid lateral tracking movement following the subject's motion from the side or at dynamic angles, maintaining continuous flow",
    "Tracking": "a precise lateral tracking shot following the subject's movement from the side or at an angle, maintaining dynamic energy",

    "Orbit Around Subject": "a smooth 360-degree orbital movement around the subject, revealing dimensional depth and perspective shifts",
    "Orbit": "a smooth 360-degree orbital movement around the subject, revealing dimensional depth and perspective shifts",

    "Slow Cinematic Pan": "a deliberate, sweeping pan across the scene from varied angles (side, diagonal, overhead), revealing layers with cinematic grace",
    "Slow Pan": "a deliberate, sweeping pan across the scene from varied angles (side, diagonal, overhead), revealing layers with cinematic grace",

    "Dolly Push In": "a forward dolly movement approaching the subject from an interesting angle (side approach, low angle rise, or diagonal), building intensity",
    "Dolly In": "a forward dolly movement approaching the subject from an interesting angle (side approach, low angle rise, or diagonal), building intensity",

    "Handheld Energy": "raw, organic handheld camera movement with natural micro-shake, capturing intimate shifting perspectives (over-shoulder, side-tracking, close details)",
    "Handheld": "raw, organic handheld camera movement with natural micro-shake, capturing intimate shifting perspectives (over-shoulder, side-tracking, close details)",

    "Static Composed Frame": "a carefully composed static frame from a creative angle (profile, three-quarter, low angle, high angle), using depth and compositional layers",
    "Static": "a carefully composed static frame from a creative angle (profile, three-quarter, low angle, high angle), using depth and compositional layers"
}

# Camera movement descriptors for visual-only mode
CAMERA_DESCRIPTORS_VISUAL = {
    "Slow Zoom In": "a slow, deliberate zoom into the visual composition",
    "Floating Camera Drift": "a floating drift through the visual space",
    "Seamless Orbit Through Scene": "a seamless circular orbit through the scene",
    "Procedural Flow Through Shapes": "a procedural flow navigating through shapes",
    "Rapid Cut Between Visual Layers": "rapid cuts between visual layers",
    "Ethereal Glide": "an ethereal gliding motion through space",
    "Fractal Tunnel Movement": "movement through a fractal tunnel effect"
}

# Mood descriptors
MOOD_DESCRIPTORS = {
    "Energetic": "fast-paced editing, vibrant color flashes, dynamic motion, and a sense of exhilarating movement",
    "Melancholic": "soft, diffused lighting, slow-motion details, a muted and desaturated color palette, and a focus on introspection",
    "Uplifting": "bright, warm lighting, sweeping camera shots, saturated, optimistic colors, and a feeling of hope and positivity",
    "Dark": "low-key lighting, deep shadows, a high-contrast and gritty look, creating a sense of mystery and tension",
    "Moody": "atmospheric and evocative lighting, rich color tones, and a focus on emotion and feeling over narrative",
    "Euphoric": "dreamlike visuals, lens flares, glowing particles, slow-motion expressions of joy, and an overwhelming sense of bliss"
}

# Subject descriptors - REVISED for dynamic movement and music video quality
SUBJECT_DESCRIPTORS = {
    # Visual-Only - NO PERFORMERS
    "None (Visual Only)": "pure abstract visual elements with NO human performers, NO dancers, NO people, NO characters. Focus entirely on light, color, texture, patterns, and motion synchronized to the music",
    # Performance / People - MUSIC VIDEO STYLE
    "Solo Dancer": "a solo dancer in mid-choreography, captured from dynamic angles (side profile, low angle, or three-quarter view), fluid athletic movement, expressive body language, NOT static posing",
    
    "Dance Duo": "two dancers in synchronized motion, interacting dynamically, captured from shifting camera perspectives, flowing movement between partners, NOT front-facing poses",
    
    "Group of Dancers": "multiple dancers in energetic choreography, captured mid-motion from varied angles (overhead, side tracking, diagonal), layered depth with staggered positioning, NOT lined up facing camera, NOT static group pose",
    
    "Singer Performing": "a vocalist in expressive performance, captured from intimate angles (profile, over-shoulder, close-up on hands/face), emotional intensity, natural movement, NOT stiff studio portrait",
    
    "DJ Performing": "a DJ actively working the decks, hands in motion on equipment, captured from dynamic angles showing both performer and gear, energetic atmosphere, NOT static pose",
    
    "Band Performing": "band members mid-performance, instruments in motion, captured with depth showing multiple performers, raw energy, interactive dynamics between musicians, NOT staged lineup",
    
    "Fashion Model": "a fashion model in motion, walking, turning, or striking dynamic poses, captured from editorial angles, confident movement, cinematic framing, NOT catalog posing",
    
    "Abstract Performer": "an abstract human form composed of light, particles, or energy, moving and transforming fluidly with the music",
    
    # Non-human / Visual
    "Light Trails": "flowing light trails that pulse, curve, and streak through space in rhythm with the music",
    "Color Gradient Flow": "smooth gradient transitions flowing dynamically across the frame with organic motion",
    "Liquid Motion": "fluid liquid forms morphing, splashing, and flowing with organic unpredictability",
    "Smoke or Ink in Water": "ethereal smoke or ink dispersing in water with natural fluid dynamics",
    "Energy Particles": "glowing energy particles swirling, pulsing, and dancing through space",
    "Abstract Geometric Shapes": "geometric shapes continuously transforming, rotating, and reconfiguring",
    "Floating 3D Objects": "3D objects suspended in space, rotating and drifting with momentum",
    "Dynamic Waves or Ripples": "rippling waves of color and light propagating through the frame",
    "Fractal or Kaleidoscope Patterns": "mesmerizing fractal patterns evolving and morphing organically",
    "Cosmic or Space Visuals": "cosmic nebula, stellar phenomena, and celestial movement"
}

# Updated setting descriptors
SETTING_DESCRIPTORS = {
    "Color Studio Background": "a clean studio with colorful gradient backgrounds",
    "Abstract Space": "a non-physical abstract dimension of light and color",
    "Gradient Wall Stage": "a stage with dynamic gradient wall projections",
    "Geometric World": "a world of geometric shapes and architectural forms",
    "Fluid Simulation Environment": "an environment of flowing fluid simulations",
    "Particle Universe": "a universe filled with glowing particles",
    "Digital Landscape": "a surreal digital landscape with neon elements",
    "Neon Tunnel": "a tunnel of pulsating neon lights",
    "Light Burst Field": "a field of bursting light rays and beams",
    "Dreamscape Environment": "a dreamlike surreal environment"
}

# Lighting style descriptors
LIGHTING_DESCRIPTORS = {
    "Soft Diffused": "gentle, even lighting with smooth shadows and cinematic depth",
    "Monochromatic Studio Light": "single-color studio lighting with subtle reflections, warm tones, and professional-grade LED setup",
    "Neon / LED": "bold colored lights with reflections and glow effects",
    "Natural Sunlight": "golden-hour sunlight with realistic shadows and soft atmospheric haze",
    "Studio Spotlights": "bright, controlled lighting emphasizing the performer",
    "Dramatic Contrast": "deep shadows and bold highlights creating visual tension",
    "Backlit Silhouette": "the subject illuminated from behind, forming a striking outline"
}

# Camera type descriptors
CAMERA_TYPE_DESCRIPTORS = {
    "35mm Anamorphic": "a cinematic 35mm anamorphic lens with elegant bokeh",
    "24mm Wide Angle": "a wide 24mm lens capturing spatial depth",
    "50mm Prime": "a crisp, natural 50mm perspective",
    "Telephoto 85mm": "an 85mm lens compressing space dramatically",
    "Handheld Camcorder": "raw handheld feel with organic movements",
    "Drone Shot": "aerial drone perspective emphasizing motion"
}

# Music video quality intent constant
MUSIC_VIDEO_INTENT = (
    "Create a PROFESSIONAL MUSIC VIDEO with cinematic production values. "
    "Emphasize dynamic camera work, varied angles, continuous motion, and artistic composition. "
    "AVOID: static poses, front-facing stances, catalog-style framing, cheesy staging, or stock-photo aesthetics. "
    "PRIORITIZE: movement, depth, creative angles, authentic energy, and editorial quality."
)

# System intent constant
SYSTEM_INTENT = (
    "System intent: Generate a professional short-form music video aligned with the provided audio. "
    "Ensure visuals feel coherent, cinematic, and emotionally aligned with the genre and mood. "
    "Output must be formatted in 9:16 portrait orientation, optimized for social platforms. "
    "Avoid text, logos, and unrealistic motion."
)

# Professional quality guarantee - injected into every prompt
CINEMATIC_DIRECTIVE = (
    "The video must have professional music-video quality with cinematic composition, dynamic motion, realistic camera depth, soft lighting, and visually engaging transitions. "
    "Shot in high-definition 4K resolution with realistic lens depth, film-grade motion blur, and professional color grading."
)

MOTION_GUARANTEE = (
    "The camera should always be moving, tracking, cutting, or panning to create depth and energy. Avoid static frames, flat angles, or slideshow visuals. "
    "Maintain filmic motion blur, depth of field, and dynamic lighting changes throughout. Every scene should feel alive with smooth parallax, lens depth, and continuous rhythm."
)

# Enhanced negative prompt constant (concise)
NEGATIVE_PROMPT = (
    "Do not include text overlays, watermarks, visual artifacts, flicker, distorted faces, or motion blur artifacts."
)

# Visual-only subject identifiers (lowercase for comparison)
VISUAL_SUBJECTS = [
    "none (visual only)", "light trails", "color gradient flow", "liquid motion",
    "smoke or ink in water", "energy particles", "abstract geometric shapes",
    "floating 3d objects", "dynamic waves or ripples", "fractal or kaleidoscope patterns",
    "cosmic or space visuals"
]


def get_style_negative_prompt(visual_style: str) -> str:
    """
    Get style-specific negative prompt to enforce visual style.
    
    Args:
        visual_style: The visual style selected by user
        
    Returns:
        Style-specific negative prompt string
    """
    style_negatives = {
        "Anime": "NOT live-action, NOT photorealistic, NOT real people, NOT cinema footage",
        "2D Illustration": "NOT photographic, NOT live-action, NOT realistic rendering, NOT cinema footage, NOT 3D",
        "Trippy": "NOT straightforward realism, NOT static composition",
        "Vintage": "NOT modern digital look, NOT clean HD"
    }
    
    return style_negatives.get(visual_style, "")


def build_enhanced_prompt(
    genre: str,
    mood: str,
    visual_style: str,
    camera_movement: str,
    duration: str,
    lighting: str,
    camera_type: str,
    creative_intensity: str,
    subject: str = "None (Visual Only)",
    setting: str = "Color Studio Background",
    extra: str = ""
) -> str:
    """
    Build an enhanced prompt for Veo 3.0 with music video quality enforcement.
    
    Supports both human performance and abstract visual-only modes.
    Includes style-specific enforcement and anti-cheesy language.
    
    Args:
        genre: Music genre
        mood: Emotional mood
        visual_style: Visual style (Cinematic, Trippy, Anime, etc.)
        camera_movement: Camera movement type
        duration: Video duration (e.g., "8s")
        lighting: Lighting style
        camera_type: Camera/lens type
        creative_intensity: Creative direction level (Precise, Balanced, Experimental)
        subject: Subject type (can be performance or visual)
        setting: Setting/environment
        extra: Additional creative notes
        
    Returns:
        Enhanced prompt string optimized for Veo 3.0
    """
    # Look up descriptors (now with improved versions)
    genre_text = GENRE_DESCRIPTORS.get(genre, genre.lower())
    style_text = STYLE_DESCRIPTORS.get(visual_style, visual_style.lower())
    mood_text = MOOD_DESCRIPTORS.get(mood, mood.lower())
    lighting_text = LIGHTING_DESCRIPTORS.get(lighting, lighting.lower())
    camera_type_text = CAMERA_TYPE_DESCRIPTORS.get(camera_type, camera_type.lower())
    
    # Get style-specific negative prompt
    style_negative = get_style_negative_prompt(visual_style)
    
    # Detect visual-only mode
    is_visual_only = subject.lower() in VISUAL_SUBJECTS
    
    # Get appropriate camera descriptor based on mode
    if is_visual_only:
        camera_text = CAMERA_DESCRIPTORS_VISUAL.get(camera_movement, camera_movement.lower())
    else:
        camera_text = CAMERA_DESCRIPTORS.get(camera_movement, camera_movement.lower())
    
    # Build scene description based on mode
    subject_text = SUBJECT_DESCRIPTORS.get(subject, subject.lower())
    setting_text = SETTING_DESCRIPTORS.get(setting, setting.lower())
    
    if is_visual_only:
        # Visual-only mode: focus on abstract visuals
        if subject == "None (Visual Only)":
            scene = f"Scene: Pure abstract visuals within {setting_text}, NO human performers, focusing on light, color, texture, and motion synchronized to the music."
        else:
            scene = f"Scene: {subject_text} flow inside {setting_text}."
    else:
        # Performance mode: feature human subjects with dynamic language
        scene = f"Scene: {subject_text} performs inside {setting_text}, captured with {camera_type_text} and {camera_movement.lower()}."
    
    # Visual style (EMPHASIZED for non-realistic styles)
    if visual_style in ["Anime", "2D Illustration"]:
        visuals = f"VISUAL MEDIUM: {visual_style.upper()}. {style_text}. Lighting style: {lighting_text}. {style_negative}"
    else:
        visuals = f"Visual style: {visual_style} with {style_text}. Lighting: {lighting_text}."
    
    # Camera and cinematography (adaptive based on mode)
    if is_visual_only:
        camera_line = f"Camera: {camera_text} with smooth transitions following the flow."
    else:
        camera_line = f"Camera work emphasizes {camera_movement.lower()}, with edits that maintain dynamic energy."
    
    # Mood
    emotion = f"Mood: {mood} — {mood_text}."
    
    # Creative intensity with logic adjustment
    if creative_intensity == "Precise":
        creative = "Direction: Precise execution with continuity and coherent motion. Polished, professional finish."
    elif creative_intensity == "Experimental":
        creative = "Direction: Experimental and bold. Embrace abstract visuals, reality-bending effects, and artistic risks."
    else:  # Balanced
        creative = "Direction: Balanced approach with creative flair and technical polish."
    
    # Extra details
    extras = f"Additional notes: {extra.strip()}." if extra.strip() else ""
    
    # Fixed 9:16 framing
    framing = "Format: Vertical 9:16 composition."
    
    # Combine all sections in narrative structure
    sections = [
        f"System intent: Generate a professional short-form vertical video aligned with the provided {genre} track.",
        scene,
        visuals,
        f"Lighting: {lighting} with {lighting_text}.",
        emotion,
        camera_line,
        creative,
        extras,
        framing,
        f"Duration: {duration}.",
        CINEMATIC_DIRECTIVE,
        MOTION_GUARANTEE,
        NEGATIVE_PROMPT
    ]
    
    full_prompt = " ".join(filter(None, sections))
    
    # Clean up whitespace
    full_prompt = " ".join(full_prompt.split()).strip()
    
    logger.info(f"Generated cinematic-quality prompt (style={visual_style}): {full_prompt[:200]}...")
    
    return full_prompt
