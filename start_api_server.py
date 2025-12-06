#!/usr/bin/env python3
"""
FastAPI Server Startup Script

Starts the ETF Analysis API server with proper Python path configuration.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now we can import with absolute paths
try:
    import uvicorn
    from api.main import app
    
    print("Starting ETF Analysis API server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Test login: testuser / testpassword")
    print("---")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        log_level="info"
    )
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    print("Try: python start_api_server.py")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)