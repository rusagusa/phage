@echo off
REM ============================================
REM  PHAGE OS - One-Click Cloud Run Deployment
REM ============================================
echo.
echo  🧬 Deploying Phage Brain to Cloud Run...
echo.

gcloud config set project project-phage
gcloud run deploy phage-gatway ^
    --source . ^
    --region europe-west1 ^
    --allow-unauthenticated ^
    --memory 512Mi

echo.
echo  ✅ Deployment complete!
echo  🌐 URL: https://phage-gatway-343327310617.europe-west1.run.app
echo.
pause
