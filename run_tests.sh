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
npm test
cd ..

echo "All tests passed successfully!"
