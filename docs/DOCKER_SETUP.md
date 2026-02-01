# 🐳 Docker Setup for Enhanced Geo-Compliance System

This guide covers the Docker setup for the enhanced geo-compliance system with spaCy integration.

## 📋 Prerequisites

- Docker and Docker Compose installed
- `.env` file with required environment variables

## 🚀 Quick Start

### 1. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 2. Test spaCy Integration

The Docker container will automatically test spaCy installation on startup. Check the logs:

```bash
# View logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend
```

### 3. Access the Services

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

## 📦 What's Included in Docker Setup

### Backend Container (`Dockerfile.backend`)

- **Python 3.11-slim** base image
- **System dependencies**: gcc, g++, curl, build-essential, python3-dev
- **spaCy installation** with `en_core_web_sm` model
- **Automatic testing** of spaCy integration on startup
- **Graceful fallback** to blank spaCy model if model download fails

### Enhanced Features

1. **Automatic spaCy Model Download**: The Docker build process downloads the required spaCy model
2. **Robust Error Handling**: If model download fails, the system falls back to a blank model
3. **Startup Testing**: Container tests spaCy integration before starting the API
4. **Enhanced Logging**: Detailed logs show spaCy setup status

## 🧪 Testing spaCy Integration

The container includes a built-in test script that runs on startup:

```bash
# Run the test manually
docker-compose exec backend python test_spacy_docker.py
```

This test will:
- ✅ Verify spaCy installation
- ✅ Check model availability (en_core_web_sm, en_core_web_md, en_core_web_lg)
- ✅ Test basic NER functionality
- ✅ Test enhanced classifier integration

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# Supabase (optional)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key

# OpenAI (optional, for enhanced LLM features)
OPENAI_API_KEY=your_openai_key
```

### Volume Mounts

The docker-compose setup includes the following volume mounts for development:

- `./backend:/app/backend` - Backend code (hot reload)
- `./regulations:/app/regulations` - Regulatory documents
- `./results:/app/results` - Results and logs

## 🐛 Troubleshooting

### spaCy Model Issues

If you see spaCy model errors:

1. **Check the logs**:
   ```bash
   docker-compose logs backend | grep spacy
   ```

2. **Manually download model**:
   ```bash
   docker-compose exec backend python -m spacy download en_core_web_sm
   ```

3. **Restart the container**:
   ```bash
   docker-compose restart backend
   ```

### Memory Issues

spaCy models require memory. If you encounter issues:

1. **Increase Docker memory limit** (Docker Desktop Settings)
2. **Use the smaller model** by modifying the Dockerfile:
   ```dockerfile
   RUN python -m spacy download en_core_web_sm
   ```

### Build Issues

If Docker build fails:

1. **Clean build cache**:
   ```bash
   docker-compose build --no-cache backend
   ```

2. **Check system dependencies**:
   ```bash
   docker-compose exec backend apt list --installed | grep -E "gcc|g++|python3-dev"
   ```

## 📊 Performance Considerations

### Model Size Comparison

| Model | Size | Features | Memory Usage |
|-------|------|----------|--------------|
| `en_core_web_sm` | ~15MB | Basic NER, POS | ~100MB |
| `en_core_web_md` | ~50MB | + Vectors | ~200MB |
| `en_core_web_lg` | ~750MB | + Large vectors | ~1GB |

**Recommendation**: Use `en_core_web_sm` for production Docker deployments.

### Optimization Tips

1. **Multi-stage builds** for smaller production images
2. **Layer caching** by copying requirements first
3. **Health checks** to ensure service availability
4. **Resource limits** in docker-compose.yml

## 🔄 Development Workflow

### 1. Code Changes

With volume mounts, code changes are reflected immediately:

```bash
# Edit files locally
vim backend/main.py

# Changes are automatically reflected in container
# (FastAPI auto-reload is enabled)
```

### 2. Adding New Dependencies

```bash
# Update requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Rebuild container
docker-compose up --build backend
```

### 3. Testing

```bash
# Run tests in container
docker-compose exec backend python -m pytest

# Run spaCy-specific tests
docker-compose exec backend python test_spacy_docker.py

# Run enhanced classifier demo
docker-compose exec backend python demo_enhanced_flow.py
```

## 📈 Production Deployment

For production deployment:

1. **Remove development mounts** from docker-compose.yml
2. **Set proper environment variables**
3. **Use production WSGI server** (already configured with uvicorn)
4. **Enable health checks** (already included)
5. **Configure logging** for your monitoring system

Example production docker-compose.yml:

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#🐛-troubleshooting) above
2. View container logs: `docker-compose logs backend`
3. Test spaCy integration: `docker-compose exec backend python test_spacy_docker.py`
4. Verify API health: `curl http://localhost:8000/health`

The enhanced geo-compliance system is designed to work robustly even if spaCy models fail to load, falling back to regex-based detection and blank spaCy models for basic functionality.
