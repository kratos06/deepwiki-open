import uvicorn
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Unified Logging Configuration ---
# Determine the project's base directory (assuming main.py is in 'api' subdirectory)
# Adjust if your structure is different, e.g., if main.py is at the root.
# This assumes 'api/main.py', so logs will be in 'api/logs/application.log'
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "application.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(lineno)d %(filename)s:%(funcName)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()  # Also keep logging to console
    ],
    force=True  # Ensure this configuration takes precedence and clears any existing handlers
)

# Get a logger for this main module (optional, but good practice)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import the api package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check for required environment variables
required_env_vars = ['GOOGLE_API_KEY', 'OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    logger.warning("Some functionality may not work correctly without these variables.")

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8001))

    # Check if MCP server should be enabled
    enable_mcp = os.environ.get("ENABLE_MCP_SERVER", "true").lower() == "true"

    logger.info(f"Starting DeepWiki API on port {port}")
    if enable_mcp:
        logger.info("MCP server integration enabled")
    else:
        logger.info("MCP server integration disabled")

    # Import the app here to ensure environment variables are set first
    # The app will now include MCP server integration via lifespan events
    from api.api import app

    # Run the FastAPI app with uvicorn
    # Disable reload in production/Docker environment
    is_development = os.environ.get("NODE_ENV") != "production"
    uvicorn.run(
        "api.api:app",
        host="0.0.0.0",
        port=port,
        reload=is_development
    )
