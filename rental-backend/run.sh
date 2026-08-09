#!/bin/bash
echo "Starting Rental Management System Backend..."

# Set OpenSSL paths for macOS (needed for cryptography package)
if [ -d "/usr/local/opt/openssl@3" ]; then
    export LDFLAGS="-L/usr/local/opt/openssl@3/lib"
    export CPPFLAGS="-I/usr/local/opt/openssl@3/include"
    export PKG_CONFIG_PATH="/usr/local/opt/openssl@3/lib/pkgconfig"
elif [ -d "/opt/homebrew/opt/openssl@3" ]; then
    export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
    export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "Starting FastAPI server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
