#!/usr/bin/env python3
"""
Development Web Server for TimeCraft UI

This module provides a simple HTTP server for serving the TimeCraft web interface
during development. It includes CORS support for API communication and automatically
opens the UI in the default web browser.

Usage:
    python serve.py

The server will start on port 8001 and serve files from the current directory.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler with CORS support.
    
    This handler adds CORS headers to responses, allowing the web interface
    to communicate with the API server running on a different port.
    """
    
    def end_headers(self):
        """Add CORS headers before ending the response headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.end_headers()

def run_server(port=8001):
    """
    Start the development web server.
    
    Args:
        port (int): Port number to listen on (default: 8001)
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f"Starting server at http://localhost:{port}")
    print(f"Access the UI at: http://localhost:{port}/scenario-timeseries.html")
    print("Press Ctrl+C to stop")
    
    # Open the browser automatically
    webbrowser.open(f'http://localhost:{port}/scenario-timeseries.html')
    
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()