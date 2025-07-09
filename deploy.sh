#!/bin/bash

# StreamFlix Deployment Script
# This script helps deploy the streaming platform to production

set -e

echo "🚀 StreamFlix Deployment Script"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to deploy with Docker
deploy_docker() {
    echo "📦 Building and deploying with Docker..."
    
    # Stop existing containers
    docker-compose down
    
    # Build and start containers
    docker-compose up --build -d
    
    echo "✅ Deployment complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:5001"
    echo "👨‍💼 Admin Panel: http://localhost:3000/admin"
}

# Function to deploy manually
deploy_manual() {
    echo "🔧 Manual deployment..."
    
    # Backend deployment
    echo "📡 Setting up backend..."
    cd streaming-backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Initialize database
    python seed_data.py
    
    # Start backend in background
    nohup python src/main.py > backend.log 2>&1 &
    echo $! > backend.pid
    
    cd ..
    
    # Frontend deployment
    echo "🎨 Setting up frontend..."
    cd streaming-frontend
    
    # Install dependencies
    pnpm install
    
    # Build for production
    pnpm run build
    
    # Start frontend in background
    nohup pnpm run preview --host > frontend.log 2>&1 &
    echo $! > frontend.pid
    
    cd ..
    
    echo "✅ Manual deployment complete!"
    echo "🌐 Frontend: http://localhost:4173"
    echo "🔧 Backend API: http://localhost:5001"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    
    # Stop Docker containers
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
    fi
    
    # Stop manual processes
    if [ -f "streaming-backend/backend.pid" ]; then
        kill $(cat streaming-backend/backend.pid) 2>/dev/null || true
        rm streaming-backend/backend.pid
    fi
    
    if [ -f "streaming-frontend/frontend.pid" ]; then
        kill $(cat streaming-frontend/frontend.pid) 2>/dev/null || true
        rm streaming-frontend/frontend.pid
    fi
    
    echo "✅ Services stopped!"
}

# Function to show logs
show_logs() {
    echo "📋 Showing logs..."
    
    if [ -f "docker-compose.yml" ] && docker-compose ps | grep -q "Up"; then
        docker-compose logs -f
    else
        echo "Backend logs:"
        tail -f streaming-backend/backend.log &
        echo "Frontend logs:"
        tail -f streaming-frontend/frontend.log &
        wait
    fi
}

# Function to check status
check_status() {
    echo "📊 Service Status:"
    echo "=================="
    
    # Check Docker containers
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        echo "Docker containers:"
        docker-compose ps
    fi
    
    # Check manual processes
    if [ -f "streaming-backend/backend.pid" ]; then
        if ps -p $(cat streaming-backend/backend.pid) > /dev/null; then
            echo "✅ Backend is running (PID: $(cat streaming-backend/backend.pid))"
        else
            echo "❌ Backend is not running"
        fi
    fi
    
    if [ -f "streaming-frontend/frontend.pid" ]; then
        if ps -p $(cat streaming-frontend/frontend.pid) > /dev/null; then
            echo "✅ Frontend is running (PID: $(cat streaming-frontend/frontend.pid))"
        else
            echo "❌ Frontend is not running"
        fi
    fi
}

# Main menu
case "$1" in
    "docker")
        deploy_docker
        ;;
    "manual")
        deploy_manual
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "status")
        check_status
        ;;
    *)
        echo "Usage: $0 {docker|manual|stop|logs|status}"
        echo ""
        echo "Commands:"
        echo "  docker  - Deploy using Docker Compose"
        echo "  manual  - Deploy manually without Docker"
        echo "  stop    - Stop all services"
        echo "  logs    - Show service logs"
        echo "  status  - Check service status"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh docker   # Deploy with Docker"
        echo "  ./deploy.sh manual   # Deploy manually"
        echo "  ./deploy.sh stop     # Stop all services"
        exit 1
        ;;
esac

