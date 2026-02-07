@echo off
echo ==========================================
echo Push to Hugging Face Space
echo ==========================================
echo.
echo This script will push your code to:
echo https://huggingface.co/spaces/subikshababu/Nataraj-Tamil-tts
echo.
echo Before running, you need a Hugging Face access token:
echo 1. Go to: https://huggingface.co/settings/tokens
echo 2. Click "New token"
echo 3. Name: Tamil-TTS-Deploy
echo 4. Role: Write
echo 5. Copy the token (starts with hf_)
echo.
set /p HF_TOKEN=Enter your Hugging Face token (hf_...): 

echo.
echo Setting remote URL with token...
git remote set-url hf https://%HF_TOKEN%@huggingface.co/spaces/subikshababu/Nataraj-Tamil-tts

echo.
echo Pushing to Hugging Face Space...
git push hf master

echo.
echo ==========================================
echo Done! Check your space at:
echo https://huggingface.co/spaces/subikshababu/Nataraj-Tamil-tts
echo ==========================================
pause
