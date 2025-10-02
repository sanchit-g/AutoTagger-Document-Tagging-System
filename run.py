"""
AutoTagger Application Entry Point
Run this file to start the Flask development server
"""
import os
from app import create_app

# Get configuration from environment or use default
config_name = os.getenv('FLASK_ENV', 'development')

# Create application instance
app = create_app(config_name)

if __name__ == '__main__':
    # Run development server
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = config_name == 'development'
    
    print(f"\n{'='*60}")
    print(f"AutoTagger API Server Starting")
    print(f"{'='*60}")
    print(f"Environment: {config_name}")
    print(f"Server: http://{host}:{port}")
    print(f"Debug Mode: {debug}")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug)