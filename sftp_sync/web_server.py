#!/usr/bin/env python
"""
Web server entry point for SFTP Sync
"""

import argparse
import uvicorn


def main():
    """Main entry point for web server"""
    parser = argparse.ArgumentParser(description="SFTP Sync Web Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"Starting SFTP Sync Web Server on http://{args.host}:{args.port}")
    print(f"API documentation available at http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        "sftp_sync.web_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
