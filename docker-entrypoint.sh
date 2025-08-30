#!/bin/bash
set -e

echo "🐳 Starting Geo-Compliance Backend in Docker"
echo "============================================="

# Test spaCy installation
echo "🧪 Testing HuggingFace NER installation..."
python test_spacy_docker.py

if [ $? -eq 0 ]; then
    echo "✅ HuggingFace tests passed, starting the application..."
else
    echo "⚠️  HuggingFace tests had issues, but continuing..."
fi

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
