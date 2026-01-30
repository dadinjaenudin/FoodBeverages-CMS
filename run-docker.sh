#!/bin/bash

# F&B POS HO System - Docker Runner Script
# Usage: ./run-docker.sh [dev|prod|stop|logs|shell]

set -e

COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="fnb-ho"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "======================================"
    echo "🍽️  F&B POS HO System - Docker"
    echo "======================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

start_dev() {
    print_header
    print_info "Starting F&B POS HO System in DEVELOPMENT mode..."
    
    check_docker
    
    # Use development compose file
    COMPOSE_FILE="docker-compose.dev.yml"
    
    # Build and start services
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    
    print_success "Development environment started!"
    print_info "Services:"
    echo "  🌐 Django App: http://localhost:8002"
    echo "  📚 API Docs (Swagger): http://localhost:8002/api/docs/"
    echo "  📖 API Docs (ReDoc): http://localhost:8002/api/redoc/"
    echo "  🔧 Admin Panel: http://localhost:8002/admin/"
    echo "  🗄️  PostgreSQL: localhost:5432"
    echo "  🔴 Redis: localhost:6379"
    echo ""
    print_info "Default Admin Credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    print_info "Use './run-docker.sh logs' to view logs"
    print_info "Use './run-docker.sh stop' to stop services"
}

start_prod() {
    print_header
    print_info "Starting F&B POS HO System in PRODUCTION mode..."
    
    check_docker
    
    # Build and start all services including nginx and monitoring
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME --profile production --profile monitoring build
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME --profile production --profile monitoring up -d
    
    print_success "Production environment started!"
    print_info "Services:"
    echo "  🌐 Nginx Proxy: http://localhost:80"
    echo "  🌐 Django App: http://localhost:8002"
    echo "  📚 API Docs (Swagger): http://localhost:8002/api/docs/"
    echo "  📖 API Docs (ReDoc): http://localhost:8002/api/redoc/"
    echo "  🔧 Admin Panel: http://localhost:8002/admin/"
    echo "  🌸 Flower (Celery Monitor): http://localhost:5555"
    echo "  🗄️  PostgreSQL: localhost:5432"
    echo "  🔴 Redis: localhost:6379"
    echo ""
    print_info "Use './run-docker.sh logs' to view logs"
    print_info "Use './run-docker.sh stop' to stop services"
}

stop_services() {
    print_header
    print_info "Stopping F&B POS HO System..."
    
    # Stop both dev and prod services
    docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME down 2>/dev/null || true
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME --profile production --profile monitoring down 2>/dev/null || true
    
    print_success "All services stopped!"
}

show_logs() {
    print_header
    print_info "Showing logs for F&B POS HO System..."
    
    # Try to show logs from either dev or prod
    if docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME ps -q web 2>/dev/null | grep -q .; then
        docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME logs -f
    elif docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps -q web 2>/dev/null | grep -q .; then
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
    else
        print_error "No running services found. Start the application first."
        exit 1
    fi
}

open_shell() {
    print_header
    print_info "Opening Django shell..."
    
    # Try to open shell in either dev or prod container
    if docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME ps -q web 2>/dev/null | grep -q .; then
        docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME exec web python manage.py shell
    elif docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps -q web 2>/dev/null | grep -q .; then
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec web python manage.py shell
    else
        print_error "No running web service found. Start the application first."
        exit 1
    fi
}

show_status() {
    print_header
    print_info "Service Status:"
    
    echo ""
    echo "Development Services:"
    docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME ps 2>/dev/null || echo "  No development services running"
    
    echo ""
    echo "Production Services:"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps 2>/dev/null || echo "  No production services running"
}

show_help() {
    print_header
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev      Start development environment (default)"
    echo "  prod     Start production environment with Nginx & monitoring"
    echo "  stop     Stop all services"
    echo "  logs     Show and follow logs"
    echo "  shell    Open Django shell"
    echo "  status   Show service status"
    echo "  help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev     # Start development environment"
    echo "  $0 prod    # Start production environment"
    echo "  $0 logs    # View logs"
    echo "  $0 stop    # Stop all services"
}

# Main script logic
case "${1:-dev}" in
    "dev")
        start_dev
        ;;
    "prod")
        start_prod
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "shell")
        open_shell
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac