#!/bin/bash

# Geo-Compliance Detection System - Docker Startup Script

set -e

# Check for development mode
DEV_MODE=${1:-"prod"}

if [ "$DEV_MODE" = "dev" ]; then
    echo "🚀 Starting Geo-Compliance Detection System in DEVELOPMENT mode..."
    echo "📝 Auto-reload enabled for both frontend and backend"
    COMPOSE_FILE="docker-compose.dev.yml"
else
    echo "🚀 Starting Geo-Compliance Detection System in PRODUCTION mode..."
    COMPOSE_FILE="docker-compose.yml"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available (try both modern and legacy)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose and try again."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE down
    echo "✅ Services stopped."
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Build and start services
echo "🔨 Building Docker images..."
$DOCKER_COMPOSE -f $COMPOSE_FILE build

echo "📦 Starting services..."
$DOCKER_COMPOSE -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
if $DOCKER_COMPOSE -f $COMPOSE_FILE ps | grep -q "healthy"; then
    echo "✅ All services are healthy!"
else
    echo "⚠️  Some services may still be starting up..."
fi

echo ""
echo "🎉 Geo-Compliance Detection System is running!"
echo ""
echo "📊 Frontend: http://localhost:8501"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""

if [ "$DEV_MODE" = "dev" ]; then
    echo "🔥 DEVELOPMENT MODE FEATURES:"
    echo "  ✨ Frontend auto-reloads when you edit frontend/app.py"
    echo "  ✨ Backend auto-reloads when you edit backend/*.py files"
    echo "  ✨ No need to rebuild containers for code changes!"
    echo ""
fi

echo "📋 Useful commands:"
echo "  View logs: $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f"
echo "  Stop services: $DOCKER_COMPOSE -f $COMPOSE_FILE down"
echo "  Restart: $DOCKER_COMPOSE -f $COMPOSE_FILE restart"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
$DOCKER_COMPOSE -f $COMPOSE_FILE logs -f
