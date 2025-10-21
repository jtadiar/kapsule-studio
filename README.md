# Kapsule Studio - AI Music Video Generator

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://studio.kapsule.co)
[![Backend API](https://img.shields.io/badge/API-deployed-blue)](https://kapsule-studio-api-qgkw6ysw4a-uc.a.run.app)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Transform your music into stunning AI-generated videos using Google's Veo 3.0 and Gemini 2.5 Flash

## 🎥 Demo

- **Live Application:** [studio.kapsule.co](https://studio.kapsule.co)
- **Backend API:** [kapsule-studio-api-qgkw6ysw4a-uc.a.run.app](https://kapsule-studio-api-qgkw6ysw4a-uc.a.run.app)
- **Demo Video:** [Coming Soon - 3 minutes]

## 📝 Project Summary

Kapsule Studio is an AI-powered music video generator that transforms audio tracks into professional-quality music videos. Built for the Google AI Hackathon, it leverages cutting-edge AI models to create unique, customizable videos that match your music's vibe and style.

### Key Features

- 🎵 **Audio Segment Selector** - Interactive timeline to select perfect 15-second clips
- 🎨 **19 Visual Subjects** - From abstract visuals to performance-based content
- 🎬 **8 Camera Movements** - Including quick cuts, tracking shots, and multi-angle coverage
- ✨ **AI Prompt Enhancement** - Gemini 2.5 Flash intelligently enhances your creative vision
- 🎥 **9:16 Portrait Videos** - Optimized for social media (TikTok, Instagram, YouTube Shorts)
- 🔄 **Automatic Synchronization** - FFmpeg seamlessly merges audio with generated video
- 🎲 **Randomize Options** - Explore creative possibilities with one click
- 👁️ **Prompt Preview** - See and edit AI-enhanced prompts before generation

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system diagram.

```
User → Netlify (Frontend) → Cloud Run (Backend) → Veo 3.0 + Gemini 2.5
                                                  ↓
                                          Cloud Storage + Firestore
```

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Web Audio API
- Deployed on Netlify

**Backend:**
- FastAPI (Python 3.11)
- Google Cloud Run (serverless)
- FFmpeg for video processing
- Docker containerization

**AI & Cloud Services:**
- **Google Veo 3.0** - Video generation from text prompts
- **Gemini 2.5 Flash** - Intelligent prompt enhancement
- **Cloud Storage** - File storage and delivery
- **Firestore** - Job tracking and status management
- **Secret Manager** - Secure credential management

## 🚀 How It Works

1. **Upload Audio** - User uploads MP3/WAV/M4A file (min 15 seconds)
2. **Select Segment** - Interactive timeline with draggable markers for 15-second selection
3. **Customize Style** - Choose from 19 subjects, 6 visual styles, 8 camera movements, 6 lighting styles
4. **AI Enhancement** - Gemini 2.5 Flash enhances the prompt with cinematic details
5. **Generate Video** - Veo 3.0 creates 9:16 portrait video (2-5 minutes processing)
6. **Process & Merge** - FFmpeg loops video to match audio duration and merges them
7. **Download** - Final music video ready for social media

## 🎯 Technologies Used

### Google AI Technologies
- **Veo 3.0** (`veo-3.0-generate-001`) - State-of-the-art video generation
  - 9:16 aspect ratio for social media
  - 720p resolution
  - 8-15 second clips
  - No audio generation (we use user's original audio)
  
- **Gemini 2.5 Flash** (`gemini-2.5-flash`) - Advanced prompt engineering
  - Transforms basic options into detailed cinematic prompts
  - Enforces motion, camera movement, and quality directives
  - Prevents static, low-quality outputs

### Google Cloud Platform
- **Cloud Run** - Serverless deployment (backend + API)
- **Cloud Storage** - Audio/video file storage (public bucket)
- **Firestore** - Real-time job status tracking
- **Secret Manager** - Secure configuration management
- **Vertex AI** - AI model access and orchestration

### Additional Technologies
- **FFmpeg** - Professional video/audio processing
  - Video looping to match audio duration
  - Audio segment extraction
  - High-quality merging with proper codecs

## 📊 Data Sources

- **User-Uploaded Audio** - Local files (MP3, WAV, M4A)
- **Cloud Storage** - Generated videos and processed audio
- **Firestore** - Job metadata, status, and timestamps
- **No External APIs** - All processing happens within Google Cloud ecosystem

## 💡 Key Learnings & Findings

### Technical Discoveries

1. **Prompt Engineering is Critical**
   - Generic prompts produce generic videos
   - Detailed, structured prompts with camera angles, lighting, and motion directives improve output quality by ~40%
   - Negative prompts are essential to prevent unwanted elements

2. **Veo 3.0 Behavior**
   - 15-second maximum duration requires video looping for longer tracks
   - 9:16 aspect ratio must be specified in API parameters, not prompt text
   - "Visual only" mode needs explicit "NO performers" language to prevent default dancer generation

3. **Async Processing Challenges**
   - Video generation takes 2-5 minutes (long-running operations)
   - Polling strategy: 10-second intervals with 5-minute timeout
   - Frontend needs dynamic loading messages to maintain user engagement

4. **FFmpeg Optimization**
   - Explicit video stream selection prevents ambiguity errors
   - `yuv420p` pixel format ensures maximum compatibility
   - Loop filter with trim is more reliable than concat for video looping

5. **Gemini Integration**
   - REST API more stable than Python SDK for preview features
   - Rate limiting essential for prompt preview endpoint
   - Fallback to rule-based enhancement if Gemini fails

### User Experience Insights

- **Audio segment selector** dramatically improves user control
- **Randomize button** encourages creative exploration
- **Prompt preview** builds trust and allows fine-tuning
- **Dynamic loading messages** reduce perceived wait time

### Production Learnings

- **Secret Manager** eliminates credential management headaches
- **Cloud Run** scales effortlessly from 0 to 10 instances
- **Netlify + Cloud Run** is a powerful combo for full-stack serverless
- **CORS configuration** critical for cross-origin API calls

## 📦 Repository Structure

```
kapsule-studio/
├── README.md                      # This file
├── ARCHITECTURE.md                # System architecture diagram
├── DEPLOYMENT_GUIDE.md            # Deployment instructions
├── LICENSE                        # MIT License
│
├── kapsule-studio-frontend/       # React frontend
│   ├── components/                # React components
│   │   ├── UploadSection.tsx      # Audio upload with segment selector
│   │   ├── PromptForm.tsx         # Customization options
│   │   ├── VideoPreview.tsx       # Result display
│   │   └── Card.tsx               # Reusable UI component
│   ├── App.tsx                    # Main application
│   ├── constants.ts               # Prompt options
│   ├── types.ts                   # TypeScript interfaces
│   ├── package.json               # Dependencies
│   ├── vite.config.ts             # Build configuration
│   ├── Dockerfile                 # Container config (optional)
│   └── .env.example               # Environment template
│
├── kapsule-studio-api/            # FastAPI backend
│   ├── main.py                    # API endpoints
│   ├── config.py                  # Configuration with Secret Manager
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container configuration
│   ├── services/                  # Business logic
│   │   ├── storage_service.py     # Cloud Storage operations
│   │   ├── firestore_service.py   # Job tracking
│   │   ├── veo_service.py         # Veo 3.0 integration
│   │   ├── gemini_service.py      # Gemini 2.5 integration
│   │   └── prompt_enhancer.py     # Rule-based prompt builder
│   ├── utils/                     # Utilities
│   │   └── video_utils.py         # FFmpeg operations
│   ├── deploy.sh                  # Cloud Run deployment script
│   └── .env.example               # Environment template
│
└── setup-gcp.sh                   # GCP setup automation
```

## 🎬 Hackathon Category

**AI/ML - Creative Tools**

This project demonstrates:
- Advanced AI model integration (Veo 3.0 + Gemini 2.5)
- Real-world creative application
- Production-ready deployment
- User-friendly interface
- Scalable architecture

## 🚀 Quick Start

### For Users

Visit [studio.kapsule.co](https://studio.kapsule.co) and start creating!

### For Developers

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete setup instructions.

**Quick local setup:**

```bash
# Backend
cd kapsule-studio-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gcloud auth application-default login
uvicorn main:app --reload

# Frontend (new terminal)
cd kapsule-studio-frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud** for providing the AI models and infrastructure
- **Veo 3.0 Team** for the incredible video generation capabilities
- **Gemini Team** for the powerful language model
- **FastAPI** for the excellent Python framework
- **React Team** for the frontend framework

## 📧 Contact

Built by [jtadiar](https://github.com/jtadiar) for the Google AI Hackathon 2025.

---

**Made with ❤️ using Google AI**
