# Gemini POC Setup Script for Windows (PowerShell)

Write-Output "🚀 Setting up Gemini LLM POC..."

# Create virtual environment
Write-Output "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
Write-Output "⚡ Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Output "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from template
Write-Output "⚙️ Setting up configuration..."
if (!(Test-Path ".env")) {
    Copy-Item "config.template" ".env"
    Write-Output "✅ Created .env file from template"
    Write-Output "📝 Please edit .env and add your GEMINI_API_KEY"
} else {
    Write-Output "⚠️ .env file already exists"
}

Write-Output ""
Write-Output "🎉 Setup complete!"
Write-Output ""
Write-Output "📝 Next steps:"
Write-Output "1. Edit .env file and add your Gemini API key"
Write-Output "2. Get API key from: https://aistudio.google.com/app/apikey"
Write-Output "3. Run test: python simple_gemini_test.py"
Write-Output ""
Write-Output "🔗 Useful commands:"
Write-Output "  python simple_gemini_test.py  # Run minimal test"
Write-Output "  python gemini_test.py         # Run full test (if rich installed)"
Write-Output ""