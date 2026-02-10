#!/bin/bash

################################################################################
# Development Environment Setup with Mock Data
################################################################################
# This script starts both the Django backend and React frontend, then populates
# the database with sample data for collaborative editing scenarios.
#
# Usage:
#   ./dev-with-mock-data.sh
#
# The script will:
#   1. Start Django development server (http://localhost:8000)
#   2. Start React development server (http://localhost:4100)
#   3. Run database migrations
#   4. Load mock data in the correct order:
#      - Users and profiles
#      - Articles with revision history
#      - Comments with threaded discussions
#      - Notifications for collaboration scenarios
#      - Follow relationships for presence indication
#
# Press Ctrl+C to stop all services.
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Backend repo is two levels up from .tara/dev-with-mock-data.sh
BACKEND_DIR="$( dirname "$SCRIPT_DIR" )"
# Workspace root is one level up from backend repo
WORKSPACE_ROOT="$( dirname "$BACKEND_DIR" )"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Dev Environment Setup${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${YELLOW}Backend directory:${NC} $BACKEND_DIR"
echo -e "${YELLOW}Frontend directory:${NC} $WORKSPACE_ROOT/jesperbesper-ai-test-repo-frontend"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"

    # Kill all background processes started by this script
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${YELLOW}Stopping Django server (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${YELLOW}Stopping React server (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    echo -e "${GREEN}Services stopped.${NC}"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

################################################################################
# Step 1: Start Django Backend
################################################################################
echo -e "${BLUE}[1/4]${NC} Starting Django development server..."
cd "$BACKEND_DIR"

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found in $BACKEND_DIR${NC}"
    exit 1
fi

# Start Django server in background
python manage.py runserver 0.0.0.0:8000 > /tmp/django.log 2>&1 &
BACKEND_PID=$!

# Wait for Django to start
echo -e "${YELLOW}Waiting for Django server to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Django server started (PID: $BACKEND_PID)${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: Django server failed to start${NC}"
        cat /tmp/django.log
        exit 1
    fi
    sleep 1
done

################################################################################
# Step 2: Start React Frontend
################################################################################
echo ""
echo -e "${BLUE}[2/4]${NC} Starting React development server..."
cd "$WORKSPACE_ROOT/jesperbesper-ai-test-repo-frontend"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found in $WORKSPACE_ROOT/jesperbesper-ai-test-repo-frontend${NC}"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start React server in background
npm start > /tmp/react.log 2>&1 &
FRONTEND_PID=$!

# Wait for React to start
echo -e "${YELLOW}Waiting for React server to start...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:4100 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ React server started (PID: $FRONTEND_PID)${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}Error: React server failed to start within timeout${NC}"
        tail -20 /tmp/react.log
        echo ""
        echo -e "${YELLOW}Continuing with mock data population (React may still be building)...${NC}"
        break
    fi
    sleep 1
done

################################################################################
# Step 3: Run Database Migrations
################################################################################
echo ""
echo -e "${BLUE}[3/4]${NC} Running database migrations..."
cd "$BACKEND_DIR"

python manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Database migrations failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Database migrations completed${NC}"

################################################################################
# Step 4: Load Mock Data
################################################################################
echo ""
echo -e "${BLUE}[4/4]${NC} Loading mock data for collaborative editing..."
echo ""

# Run all population commands in the correct order:
# 1. Users and profiles (foundational)
# 2. Articles with revision history
# 3. Comments with threaded discussions
# 4. Notifications for collaboration
# 5. Follow relationships for presence

cd "$BACKEND_DIR"

echo -e "${YELLOW}Loading users and profiles...${NC}"
python manage.py load_users
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to load users${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Users and profiles loaded${NC}"

echo ""
echo -e "${YELLOW}Loading articles with revision history...${NC}"
python manage.py load_articles
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to load articles${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Articles loaded${NC}"

echo ""
echo -e "${YELLOW}Loading comments with threaded discussions...${NC}"
python manage.py load_comments
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to load comments${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Comments loaded${NC}"

echo ""
echo -e "${YELLOW}Loading notifications for collaboration scenarios...${NC}"
python manage.py load_notifications
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to load notifications${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Notifications loaded${NC}"

echo ""
echo -e "${YELLOW}Loading collaboration relationships...${NC}"
python manage.py load_collaboration_relationships
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to load collaboration relationships${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Collaboration relationships loaded${NC}"

################################################################################
# Startup Complete
################################################################################
echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Development environment is ready!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${BLUE}Available Services:${NC}"
echo -e "  ${YELLOW}Backend (Django):${NC}   http://localhost:8000"
echo -e "  ${YELLOW}Frontend (React):${NC}   http://localhost:4100"
echo ""
echo -e "${BLUE}Mock Data Loaded:${NC}"
echo -e "  • 5 users (alice, bob, charlie, diana, eve) with profiles"
echo -e "  • 3 articles with revision history (v1, v2, v3)"
echo -e "  • Threaded comment discussions with @mentions"
echo -e "  • Notifications for mentions, comments, follows, and collaboration"
echo -e "  • Follow relationships establishing collaboration network"
echo ""
echo -e "${BLUE}Backend Logs:${NC}   /tmp/django.log"
echo -e "${BLUE}Frontend Logs:${NC}   /tmp/react.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services.${NC}"
echo ""

# Keep the script running
wait
