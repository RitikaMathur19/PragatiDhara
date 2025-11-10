@echo off
REM Gemini POC Setup Script for Windows (Batch)

echo 🚀 Setting up Gemini LLM POC...

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ⚡ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Create .env from template
echo ⚙️ Setting up configuration...
if not exist ".env" (
    copy "config.template" ".env"
    echo ✅ Created .env file from template
    echo 📝 Please edit .env and add your GEMINI_API_KEY
) else (
    echo ⚠️ .env file already exists
)

echo.
echo 🎉 Setup complete!
echo.
echo 📝 Next steps:
echo 1. Edit .env file and add your Gemini API key
echo 2. Get API key from: https://aistudio.google.com/app/apikey
echo 3. Run test: python simple_gemini_test.py
echo.
echo 🔗 Useful commands:
echo   python simple_gemini_test.py  # Run minimal test
echo   python gemini_test.py         # Run full test (if rich installed)
echo.
pause