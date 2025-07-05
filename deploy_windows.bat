@echo off
:: Windows script to deploy the application

echo Testing backend...
cd backend
python -m uvicorn server:app --host 127.0.0.1 --port 8080 &
timeout /t 3 /nobreak > nul

:: Test the API
curl -s http://localhost:8080/
if %ERRORLEVEL% neq 0 (
    echo Backend health check failed
    exit /b 1
)

echo Backend test passed. Preparing for deployment...

:: Build frontend
cd ..\frontend
npm run build

echo Deployment preparation complete!
echo.
echo To deploy:
echo 1. Push your code to GitHub
echo 2. Deploy the backend on Render (see DEPLOYMENT.md)
echo 3. Deploy the frontend on Vercel (see DEPLOYMENT.md)
echo.
echo Once deployed, update the frontend .env.production file with your backend URL.
