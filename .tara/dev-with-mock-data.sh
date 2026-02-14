```bash
#!/bin/bash

################################################################################
# Full Development Environment Setup Script
################################################################################
# This script:
#
# - Sets up Python virtual environment
# - Installs backend dependencies
# - Loads environment variables (.env if present)
# - Runs migrations
# - Starts Django backend
# - Installs frontend dependencies
# - Starts React frontend
# - Loads mock data if available
#
# Designed to run locally OR inside Docker.
################################################################################

set -e

################################################################################
# Colors
################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

################################################################################
# Directory detection
################################################################################

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( dirname "$SCRIPT_DIR" )"
WORKSPACE_ROOT="$( dirname "$BACKEND_DIR" )"

FRONTEND_DIR="$WORKSPACE_ROOT/react-redux-realworld-example-app"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Dev Environment Setup${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${YELLOW}Backend:${NC} $BACKEND_DIR"
echo -e "${YELLOW}Frontend:${NC} $FRONTEND_DIR"
echo ""

################################################################################
# Cleanup
################################################################################

cleanup() {

    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"

    if [ ! -z "$BACKEND_PID" ]; then
        kill -TERM $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        kill -TERM $FRONTEND_PID 2>/dev/null || true
    fi

    echo -e "${GREEN}Shutdown complete${NC}"
}

trap cleanup EXIT INT TERM

################################################################################
# Backend setup
################################################################################

echo -e "${BLUE}[1/6] Backend setup${NC}"

cd "$BACKEND_DIR"

if [ ! -f "manage.py" ]; then
    echo -e "${RED}manage.py not found${NC}"
    exit 1
fi

################################################################################
# Load environment variables
################################################################################

if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading .env file${NC}"
    export $(grep -v '^#' .env | xargs)
fi

################################################################################
# Virtual environment
################################################################################

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment${NC}"
    python3 -m venv venv
fi

echo -e "${YELLOW}Activating virtual environment${NC}"
source venv/bin/activate || source venv/Scripts/activate

################################################################################
# Install dependencies
################################################################################

echo -e "${YELLOW}Installing backend dependencies${NC}"

if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
fi

################################################################################
# Run migrations BEFORE starting server
################################################################################

echo -e "${BLUE}[2/6] Running migrations${NC}"

python manage.py migrate

echo -e "${GREEN}Migrations complete${NC}"

################################################################################
# Optional superuser
################################################################################

if python manage.py shell -c "import django.contrib.auth; exit()" 2>/dev/null; then

    echo -e "${YELLOW}Ensuring default superuser exists${NC}"

    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
EOF

fi

################################################################################
# Start backend
################################################################################

echo -e "${BLUE}[3/6] Starting Django${NC}"

python manage.py runserver 0.0.0.0:8000 > /tmp/django.log 2>&1 &
BACKEND_PID=$!

echo -e "${YELLOW}Waiting for Django...${NC}"

for i in {1..30}; do

    if curl -s http://localhost:8000 >/dev/null; then
        echo -e "${GREEN}Django running${NC}"
        break
    fi

    sleep 1

done

################################################################################
# Frontend setup
################################################################################

echo -e "${BLUE}[4/6] Frontend setup${NC}"

if [ -d "$FRONTEND_DIR" ]; then

    cd "$FRONTEND_DIR"

    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi

    echo -e "${BLUE}[5/6] Starting React${NC}"

    npm start > /tmp/react.log 2>&1 &
    FRONTEND_PID=$!

else

    echo -e "${YELLOW}Frontend directory not found, skipping${NC}"

fi

################################################################################
# Load mock data if commands exist
################################################################################

echo -e "${BLUE}[6/6] Loading mock data${NC}"

cd "$BACKEND_DIR"

for cmd in \
    load_users \
    load_articles \
    load_comments \
    load_notifications \
    load_collaboration_relationships
do

    if python manage.py help | grep -q "$cmd"; then

        echo -e "${YELLOW}Running $cmd${NC}"
        python manage.py $cmd

    fi

done

################################################################################
# Success output
################################################################################

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Environment ready${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:4100"
echo ""
echo "Logs:"
echo "  /tmp/django.log"
echo "  /tmp/react.log"
echo ""
echo "Press Ctrl+C to stop"
echo ""

wait
```
