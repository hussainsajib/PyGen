import logging

logging.basicConfig(
    level=logging.DEBUG,  # Log level can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Format of logs
    handlers=[
        logging.FileHandler("app.log"),   # Log to a file
        logging.StreamHandler()           # Log to console
    ]
)
logger = logging.getLogger("PyGen")
