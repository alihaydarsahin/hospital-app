import os
from app import create_app
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Determine application environment
env = os.environ.get('FLASK_ENV', 'development')

# Create application
app = create_app()

if __name__ == '__main__':
    # Enable debug mode only in development environment
    debug = env == 'development'
    
    # Get port number from .env file or use default 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',  # Allow access from all IPs
        port=port,
        debug=debug
    ) 