# Step-by-Step Deployment Tutorial

This tutorial provides detailed steps with screenshots for deploying the CPS Learning System to Render and Vercel.

## Backend Deployment on Render

### 1. Create a Render Account

- Go to [Render](https://render.com/) and sign up with your GitHub account.

### 2. Create a New Web Service

- From your Render dashboard, click "New +"
- Select "Web Service"

### 3. Connect Your Repository

- Connect your GitHub repository
- Find and select your CPS Learning System repository

### 4. Configure the Service

- **Name**: cps-learning-backend
- **Region**: Choose the closest to your users
- **Branch**: main (or your default branch)
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `bash start.sh`

### 5. Add Environment Variables

- Scroll down to the "Environment" section
- Add the following variables:
  - `MONGODB_URI`: Your MongoDB Atlas connection string
  - `DATABASE_NAME`: cps_learning_system
  - `GROQ_API_KEY`: Your Groq API key

### 6. Create the Web Service

- Click "Create Web Service"
- Render will begin deploying your backend

### 7. Verify Deployment

- Once deployed, visit your service URL (e.g., `https://cps-learning-backend.onrender.com`)
- You should see a JSON response with a "healthy" status

## Frontend Deployment on Vercel

### 1. Create a Vercel Account

- Go to [Vercel](https://vercel.com/) and sign up with your GitHub account

### 2. Import Your Repository

- Click "Add New..."
- Select "Project"
- Import your GitHub repository

### 3. Configure the Project

- **Framework Preset**: Vite
- **Root Directory**: frontend (if your frontend code is in a subdirectory)
- **Build Command**: `npm run build`
- **Output Directory**: dist

### 4. Add Environment Variables

- Click on "Environment Variables"
- Add the following variable:
  - `VITE_API_URL`: Your Render backend URL (e.g., https://cps-learning-backend.onrender.com)

### 5. Deploy

- Click "Deploy"
- Vercel will build and deploy your frontend

### 6. Verify Deployment

- Once deployed, visit your Vercel deployment URL
- You should see your CPS Learning System frontend
- Test the login and chat functionality

## Connecting MongoDB Atlas

### 1. Create a MongoDB Atlas Account

- Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Sign up for a free account

### 2. Create a Cluster

- Click "Build a Cluster"
- Select the free tier option
- Choose a cloud provider and region
- Click "Create Cluster"

### 3. Set Up Database Access

- In the left sidebar, click "Database Access"
- Click "Add New Database User"
- Create a username and password
- Set user privileges to "Read and write to any database"
- Click "Add User"

### 4. Set Up Network Access

- In the left sidebar, click "Network Access"
- Click "Add IP Address"
- Select "Allow Access from Anywhere" (for development)
- Click "Confirm"

### 5. Get Connection String

- Go back to your cluster
- Click "Connect"
- Select "Connect your application"
- Copy the connection string
- Replace `<password>` with your database user's password

### 6. Add to Render Environment Variables

- Go to your backend service on Render
- Add the connection string as the `MONGODB_URI` environment variable

## Groq API Setup

### 1. Create a Groq Account

- Go to [Groq](https://console.groq.com/)
- Sign up for an account

### 2. Get API Key

- Navigate to API Keys section
- Create a new API key
- Copy the API key

### 3. Add to Render Environment Variables

- Go to your backend service on Render
- Add the API key as the `GROQ_API_KEY` environment variable

## Updating Your Deployment

### Backend Updates

- Push changes to your GitHub repository
- Render will automatically redeploy your backend

### Frontend Updates

- Push changes to your GitHub repository
- Vercel will automatically redeploy your frontend

---

Your CPS Learning System should now be fully deployed and accessible online!
