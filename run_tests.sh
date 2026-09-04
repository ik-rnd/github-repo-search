#!/bin/bash
set -e

echo "Running backend tests..."
cd backend
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
python -m pytest
cd ..

echo "Running frontend tests..."
cd frontend
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
npm test
cd ..

echo "All tests passed successfully!"
