import os
import sys

# Ensure root directory is on Python module search path for Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Entrypoint for Vercel Serverless Functions
app = app
