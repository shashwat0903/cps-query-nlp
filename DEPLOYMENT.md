# CPS Learning System Deployment Guide

This guide provides instructions for deploying the CPS Learning System backend and frontend for free using Render and Vercel.

## Prerequisites

- GitHub account (to push your code)
- Render account (for backend)
- Vercel account (for frontend)
- MongoDB Atlas account (for database)
- Groq API key (for AI chat)

## Step 1: Set up MongoDB Atlas

1. Create a free MongoDB Atlas account at https://www.mongodb.com/cloud/atlas/register
2. Create a new cluster (the free tier is sufficient)
3. Create a database user with read and write permissions
4. Whitelist all IP addresses (0.0.0.0/0) for development or add specific IPs for production
5. Get your MongoDB connection string, which will look like:
   ```
   mongodb+srv://<username>:<password>@<cluster-url>/<dbname>?retryWrites=true&w=majority
   ```

## Step 2: Deploy the Backend on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - **Name**: cps-learning-backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash start.sh`
4. Add the following environment variables:
   - `MONGODB_URI`: Your MongoDB Atlas connection string
   - `DATABASE_NAME`: cps_learning_system
   - `GROQ_API_KEY`: Your Groq API key
5. Deploy the service

## Step 3: Deploy the Frontend on Vercel

1. Create a new project on Vercel
2. Connect your GitHub repository
3. Configure the project:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: dist
4. Add the following environment variable:
   - `VITE_API_URL`: Your Render backend URL (e.g., https://cps-learning-backend.onrender.com)
5. Deploy the project

## Step 4: Configure CORS (if needed)

If you experience CORS issues, update the backend's CORS configuration in `server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing the Deployment

1. Visit your Vercel frontend URL
2. The application should connect to the backend and function properly
3. Test user registration, login, and chat functionality

## Troubleshooting

- **Backend not responding**: Check Render logs for errors
- **Frontend not connecting to backend**: Verify the VITE_API_URL environment variable
- **Database errors**: Check MongoDB Atlas connection and network access settings
- **CORS errors**: Update the CORS configuration in the backend

## Updating the Deployment

- Push changes to your GitHub repository
- Render and Vercel will automatically redeploy your application
