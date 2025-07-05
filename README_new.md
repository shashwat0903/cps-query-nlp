# CPS Learning System - AI-Powered Data Structures & Algorithms Learning Assistant

Inspired by intelligent systems like YouTube and Netflix, the **Concept Positioning System (CPS)** is designed to assist learners in mastering advanced Data Structures & Algorithms (DSA) by identifying their knowledge gaps and dynamically recommending tailored micro-learning paths through prerequisite-driven concept graphs.

## 🚀 Features

- **AI-Powered Chat Interface**: Engage with an intelligent assistant specialized in DSA topics
- **Personalized Learning Paths**: Get customized learning recommendations based on your knowledge gaps
- **Topic Graph Analysis**: Advanced concept mapping to understand prerequisites and relationships
- **Video Resource Integration**: Curated YouTube video recommendations for each topic
- **User Progress Tracking**: Monitor your learning journey and topic mastery
- **Responsive Design**: Seamless experience across desktop and mobile devices

## 🔧 Tech Stack

### Backend
- FastAPI (Python)
- MongoDB for data persistence
- Groq AI API for natural language understanding
- NetworkX for graph analysis
- YouTube API integration

### Frontend
- React + TypeScript
- Tailwind CSS for styling
- Context API for state management
- Vite for fast development and building

## 📋 Installation and Setup

### Prerequisites
- Node.js (v16 or later)
- Python 3.8+
- MongoDB
- Groq API key

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Set up environment variables
cp .env.example .env
# Edit .env with your MongoDB URI and Groq API key
python server.py
```

### Frontend Setup
```bash
cd frontend
npm install
# Set up environment variables
cp .env.example .env
# Edit .env with your backend API URL
npm run dev
```

## 📊 Project Structure

```
├── backend/
│   ├── database/           # MongoDB integration
│   ├── queryHandling/      # AI chat and graph analysis
│   ├── routes/             # API endpoints
│   └── server.py           # Main FastAPI application
│
└── frontend/
    ├── public/             # Static assets
    ├── src/
    │   ├── components/     # Reusable UI components
    │   ├── contexts/       # React Context providers
    │   ├── pages/          # Main application pages
    │   ├── services/       # API services
    │   └── utils/          # Helper functions
    └── index.html          # Entry HTML file
```

## 🚀 Deployment

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md) and [DEPLOYMENT_TUTORIAL.md](DEPLOYMENT_TUTORIAL.md).

## 👥 Contributors

- Ritesh Singh
- Shashwat ([@shashwat0903](https://github.com/shashwat0903))
- Chirag Khairnar (Team Lead)
- Shreya Ojha 
- Aditi Mishra
- Goutam

## 🙏 Acknowledgments

- Special thanks to our mentors and advisors
- Groq for providing the AI API
- MongoDB for database services
