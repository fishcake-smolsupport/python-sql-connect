import os
import logging
import datetime
from functools import wraps

# Create log directory if it doesn't exist
log_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')
os.makedirs(log_directory, exist_ok=True)

# Configure logging
filename = os.path.join(log_directory, 'app.log')
logging.basicConfig(
    filename=filename,
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


# Logger decorator
def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from datetime import datetime, timezone
        called_at = datetime.now(timezone.utc)
        logging.info(f"Running {func.__name__!r} function.")
        try:
            result = func(*args, **kwargs)
            logging.info(f"Function {func.__name__!r} executed successfully.")
            return result
        except Exception as e:
            logging.error(f"Error in function {func.__name__!r} at {called_at}: {e}")
            raise
    return wrapper

