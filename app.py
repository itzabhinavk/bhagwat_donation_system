"""
app.py - Main Flask Application Entry Point
This is the main file that creates and runs the Flask app.
"""
from flask import Flask
from config import Config

def create_app():
    """Application factory function - creates and configures Flask app."""
    app = Flask(__name__)

    # Load configuration from Config class
    app.config.from_object(Config)

    # Register Blueprints (route modules)
    from routes.public import public_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    return app


# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Run in debug mode locally (never use debug=True in production)
    app.run(debug=True, host='0.0.0.0', port=5000)
