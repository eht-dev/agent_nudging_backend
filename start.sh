#!/bin/bash
echo "🚀 Starting Universal Multi-Agent Platform Backend"

# Function to check Python version
check_python_version() {
   local python_cmd=$1
   if command -v $python_cmd &> /dev/null; then
       local version=$($python_cmd --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
       echo $version
   else
       echo "none"
   fi
}

# Find compatible Python version (3.8 to 3.12)
PYTHON_CMD=""
for py_version in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
   version=$(check_python_version $py_version)
   if [[ "$version" != "none" ]]; then
       major=$(echo $version | cut -d'.' -f1)
       minor=$(echo $version | cut -d'.' -f2)
       if [[ $major -eq 3 ]] && [[ $minor -ge 8 ]] && [[ $minor -le 12 ]]; then
           PYTHON_CMD=$py_version
           echo "✅ Found compatible Python: $py_version ($version)"
           break
       fi
   fi
done

if [[ -z "$PYTHON_CMD" ]]; then
   echo "❌ No compatible Python version found (3.8-3.12 required)"
   echo "📦 Please install Python 3.11 or 3.12:"
   echo "   brew install python@3.11  # macOS"
   echo "   sudo apt install python3.11  # Ubuntu"
   exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
   echo "Creating virtual environment with $PYTHON_CMD..."
   $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
if pip install -r requirements.txt; then
   echo "✅ All dependencies installed successfully"
else
   echo "⚠️ Some packages failed to install. This is normal for optional dependencies."
   echo "✅ Core functionality should still work"
fi

# Verify FastAPI installation
if python -c "import fastapi" 2>/dev/null; then
   echo "✅ FastAPI installation verified"
else
   echo "❌ FastAPI installation failed - trying manual install..."
   pip install fastapi uvicorn
   if python -c "import fastapi" 2>/dev/null; then
       echo "✅ FastAPI installed successfully"
   else
       echo "❌ Critical error: Cannot install FastAPI"
       exit 1
   fi
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if main.py exists
if [ ! -f "main.py" ]; then
   echo "❌ main.py not found in current directory"
   echo "📁 Make sure you're in the correct project directory"
   exit 1
fi

# Check if .env file exists, if not create a basic one
if [ ! -f ".env" ]; then
   echo "📝 Creating basic .env file..."
   cat > .env << 'EOF'
DATABASE_URL=postgresql://root:password@localhost:5432/lms_nudging_system
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
LLM_PROVIDER=ollama
API_HOST=0.0.0.0
API_PORT=8000
EOF
   echo "✅ Created .env file with default settings"
   echo "⚠️  Please update database credentials in .env file"
fi

# Run the application
echo ""
echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🌐 API Base URL: http://localhost:8000"
echo "💾 Health Check: http://localhost:8000/health"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python main.py