#!/bin/bash
set -e

echo "Running backend tests..."
cd backend
# Make sure to run in the virtual environment if it exists, or just use pytest directly.
pytest
cd ..

echo "Running frontend tests..."
cd frontend
npm test
cd ..

echo "All tests passed successfully!"
