# 🚀 Deployment Checklist for Google Cloud Run Hackathon

**Project:** Kapsule Studio - AI Music Video Generator  
**Deadline:** Contest ends - Check contest dates  
**Status:** ⏳ In Development - NOT YET DEPLOYED

---

## ⚠️ CRITICAL: Security Before Deployment

### 🔐 Secret Manager Setup (MUST DO FIRST)

- [ ] **Enable Secret Manager API**
  ```bash
  gcloud services enable secretmanager.googleapis.com
  ```

- [ ] **Create secrets in Secret Manager**
  ```bash
  echo -n "kapsule-stitch-public" | gcloud secrets create gcs-bucket-name --data-file=-
  echo -n "gen-lang-client-0915852466" | gcloud secrets create gcp-project-id --data-file=-
  # Add any other sensitive configs as needed
  ```

- [ ] **Grant Cloud Run access to secrets**
  ```bash
  PROJECT_NUMBER=$(gcloud projects describe gen-lang-client-0915852466 --format="value(projectNumber)")
  SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  
  gcloud secrets add-iam-policy-binding gcs-bucket-name \
      --member="serviceAccount:${SERVICE_ACCOUNT}" \
      --role="roles/secretmanager.secretAccessor"
  ```

- [ ] **Update `config.py` to use Secret Manager**
  - Add function to access secrets
  - Update all sensitive variables to pull from Secret Manager
  - Keep local dev fallback with `.env` file

- [ ] **Remove ALL sensitive files from git history**
  ```bash
  # Check for any committed secrets
  git log --all --full-history -- "*.json"
  git log --all --full-history -- ".env"
  
  # If found, use git filter-branch to remove them
  # BE CAREFUL - This rewrites history
  ```

---

## 📋 Pre-Deployment Code Changes

### Backend API (`kapsule-studio-api/`)

- [ ] **Update `.gitignore`**
  ```
  venv/
  *.pyc
  __pycache__/
  .env
  *.log
  gcp-key.json
  *.pem
  *.key
  credentials.json
  .DS_Store
  ```

- [ ] **Verify `.dockerignore`**
  ```
  venv/
  *.pyc
  __pycache__/
  .env
  .git/
  *.json
  *.log
  .DS_Store
  ```

- [ ] **Update `config.py` for Secret Manager** (see security section)

- [ ] **Test locally with Application Default Credentials**
  ```bash
  gcloud auth application-default login
  python main.py
  ```

- [ ] **Add health check endpoint** (already exists at `/`)

- [ ] **Set proper CORS origins** (update to Cloud Run URLs after deployment)

### Frontend (`kapsule-studio-frontend/`)

- [ ] **Create `Dockerfile`** for frontend
  - Multi-stage build with Node.js
  - Serve with nginx
  - Expose port 8080

- [ ] **Create `nginx.conf`** for frontend
  - Listen on port 8080
  - Serve static files
  - Handle SPA routing

- [ ] **Create `.dockerignore`** for frontend
  ```
  node_modules/
  .git/
  .env
  .DS_Store
  dist/
  ```

- [ ] **Update API URL environment variable**
  - Will be set during Cloud Run deployment
  - Point to backend Cloud Run URL

---

## 🏗️ Backend Deployment Steps

- [ ] **Build and push backend Docker image**
  ```bash
  cd kapsule-studio-api
  gcloud builds submit --tag gcr.io/gen-lang-client-0915852466/kapsule-studio-api
  ```

- [ ] **Deploy backend to Cloud Run**
  ```bash
  gcloud run deploy kapsule-studio-api \
    --image gcr.io/gen-lang-client-0915852466/kapsule-studio-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --timeout 600 \
    --cpu 2 \
    --set-env-vars GCP_PROJECT_ID=gen-lang-client-0915852466,GCP_REGION=us-central1 \
    --max-instances 10
  ```

- [ ] **Get backend URL**
  ```bash
  gcloud run services describe kapsule-studio-api --region us-central1 --format="value(status.url)"
  ```

- [ ] **Test backend endpoint**
  ```bash
  curl https://kapsule-studio-api-xxxxx-uc.a.run.app/
  # Should return: {"status":"healthy",...}
  ```

---

## 🎨 Frontend Deployment Steps

- [ ] **Build and push frontend Docker image**
  ```bash
  cd kapsule-studio-frontend
  gcloud builds submit --tag gcr.io/gen-lang-client-0915852466/kapsule-studio-frontend
  ```

- [ ] **Deploy frontend to Cloud Run**
  ```bash
  gcloud run deploy kapsule-studio-frontend \
    --image gcr.io/gen-lang-client-0915852466/kapsule-studio-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --timeout 300 \
    --set-env-vars VITE_API_URL=https://kapsule-studio-api-xxxxx-uc.a.run.app \
    --max-instances 10
  ```

- [ ] **Get frontend URL**
  ```bash
  gcloud run services describe kapsule-studio-frontend --region us-central1 --format="value(status.url)"
  ```

- [ ] **Update backend CORS to allow frontend URL**
  - Update `config.py` FRONTEND_URL
  - Redeploy backend

- [ ] **Test full application**
  - Visit frontend URL
  - Upload audio
  - Generate video
  - Verify download works

---

## 📝 GitHub Repository Preparation

- [ ] **Create public GitHub repository**
  - Name: `kapsule-studio` or similar

- [ ] **Ensure clean git history**
  - No sensitive files
  - No API keys or credentials
  - No `venv/` or `node_modules/`

- [ ] **Create comprehensive `README.md`**
  - Project description
  - Architecture overview
  - Technologies used (Veo, Cloud Run, GCS, Firestore)
  - Setup instructions
  - Deployment instructions
  - Demo video link

- [ ] **Create `ARCHITECTURE.md`** with diagram
  - Visual flow diagram
  - Show: Frontend → Backend → Veo/GCS/Firestore
  - Explain Cloud Run services architecture

- [ ] **Update all documentation**
  - Installation steps
  - Configuration instructions
  - API endpoints documentation
  - Frontend component overview

- [ ] **Add LICENSE file** (MIT recommended)

- [ ] **Push to GitHub**
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/kapsule-studio.git
  git push -u origin main
  ```

---

## 🎥 Demo Video Preparation (3 mins max)

- [ ] **Record screen showing:**
  1. **Intro** (15 sec) - What is Kapsule Studio?
  2. **Upload audio** (30 sec) - Show file upload
  3. **Select options** (30 sec) - Genre, mood, style, etc.
  4. **Generate video** (45 sec) - Show processing, explain Veo usage
  5. **Download result** (30 sec) - Play generated 9:16 video
  6. **Architecture** (30 sec) - Show Cloud Run services, explain backend

- [ ] **Upload to YouTube** (set as Public or Unlisted)

- [ ] **Add English subtitles** (if needed)

- [ ] **Get shareable link**

---

## 📊 Hackathon Submission on Devpost

### Required Components:

- [ ] **Select Category:** GPU Category (uses Veo model) or AI Agents Category

- [ ] **Project Title:** "Kapsule Studio - AI Music Video Generator"

- [ ] **Tagline:** "Transform audio into stunning 9:16 music videos using Google Veo 3.0"

- [ ] **Description:** (comprehensive text description)
  - Problem statement
  - Solution overview
  - Technologies: Cloud Run, Veo 3.0, Firestore, GCS, FFmpeg
  - Architecture explanation
  - Key features: Portrait mode, auto-looping, enhanced prompts
  - Challenges overcome
  - Future improvements

- [ ] **GitHub Repository URL:** https://github.com/YOUR_USERNAME/kapsule-studio

- [ ] **Live Demo URL:** https://kapsule-studio-frontend-xxxxx.run.app

- [ ] **Demo Video URL:** https://youtube.com/watch?v=xxxxx

- [ ] **Architecture Diagram:** (upload image or link)

- [ ] **Built With Tags:**
  - Google Cloud Run
  - Google Veo
  - Python
  - FastAPI
  - React
  - TypeScript
  - Firestore
  - Cloud Storage
  - FFmpeg

---

## 🎁 Bonus Points Submissions

- [ ] **Blog Post** (+0.4 points)
  - Platform: Medium, Dev.to, or personal blog
  - Title: "Building an AI Music Video Generator with Google Veo and Cloud Run"
  - Content: Architecture, challenges, code snippets, learnings
  - Must mention: "Created for #CloudRunHackathon"
  - Make PUBLIC (not unlisted)
  - Submit URL in Devpost

- [ ] **Social Media Post** (+0.4 points)
  - Platform: X (Twitter), LinkedIn, Instagram, or Facebook
  - Content: Screenshot + demo link + description
  - **Must include:** #CloudRunHackathon
  - Submit URL in Devpost

---

## ✅ Final Verification Before Submission

- [ ] **Test full workflow end-to-end**
  - Frontend loads
  - Audio upload works
  - Video generation completes
  - Download works
  - No errors in Cloud Run logs

- [ ] **Check Cloud Run logs**
  ```bash
  gcloud run logs read kapsule-studio-api --region us-central1 --limit 50
  gcloud run logs read kapsule-studio-frontend --region us-central1 --limit 50
  ```

- [ ] **Verify no secrets in public repo**
  ```bash
  git log --all --full-history -- "*.json"
  git log --all --full-history -- ".env"
  ```

- [ ] **Test with fresh browser** (incognito mode)

- [ ] **Mobile responsive check** (for 9:16 video display)

- [ ] **All submission fields completed on Devpost**

- [ ] **Review submission one final time before deadline**

---

## 🎯 Scoring Maximization

**Technical Implementation (40%)**
- ✅ Clean, documented code
- ✅ Proper error handling
- ✅ Scalable architecture
- ✅ Efficient Cloud Run usage

**Demo and Presentation (40%)**
- ✅ Clear problem definition
- ✅ Effective demo video
- ✅ Architecture diagram
- ✅ Comprehensive documentation

**Innovation and Creativity (20%)**
- ✅ Novel use of Veo for music videos
- ✅ Portrait mode optimization
- ✅ Auto-looping video matching audio
- ✅ Enhanced prompt system

**Bonus Points (1.6 total)**
- ✅ Uses Veo model (+0.4)
- ✅ Multiple Cloud Run services (+0.4)
- ✅ Blog post (+0.4)
- ✅ Social media (+0.4)

**Target Score:** 6.6 / 6.6 🏆

---

## 📞 Support Contacts

- **Cloud Run Issues:** https://cloud.google.com/run/docs
- **Veo Documentation:** https://cloud.google.com/vertex-ai/docs
- **Hackathon Support:** Via Devpost messaging
- **Contest Rules:** run.devpost.com

---

## ⏰ Important Dates

- [ ] **Submission Deadline:** Check contest site for exact date/time
- [ ] **Winner Announcement:** ~December 12, 2025
- [ ] **Credit Request Deadline:** November 7th, 12:00 PM PT (if needed)

---

**Status:** 🟡 IN DEVELOPMENT - Complete this checklist before deployment!

**Last Updated:** 2025-10-20

---

## 📌 Notes

- Keep local development environment working throughout
- Test Secret Manager integration locally before deploying
- Budget for Cloud Run costs (should be minimal with $100 credit)
- Save all deployment commands and outputs
- Document any issues encountered for blog post

