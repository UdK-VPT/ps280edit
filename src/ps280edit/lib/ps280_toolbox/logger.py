import logging
import sys

# Clear any default root logger handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Create a custom logger
logger = logging.getLogger("stderr_logger")
logger.setLevel(logging.DEBUG)  # Capture all levels

# Prevent duplication by disabling propagation
logger.propagate = False

# Create handlers
stdout_handler = logging.StreamHandler(sys.stdout)
stderr_handler = logging.StreamHandler(sys.stderr)

# Set levels for handlers
stdout_handler.setLevel(logging.INFO)   # INFO and below
stderr_handler.setLevel(logging.ERROR)  # ERROR and above

# Create formatters and add them to handlers
stderrformatter = logging.Formatter('%(levelname)s: - %(message)s')
stdoutformatter = logging.Formatter('%(levelname)s: - %(message)s')
stdout_handler.setFormatter(stdoutformatter)
stderr_handler.setFormatter(stderrformatter)

# Add handlers to the logger
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)

## Test logging at different levels
#logger.debug("This is a DEBUG message")
#logger.info("This is an INFO message")
#logger.warning("This is a WARNING message")
#logger.error("This is an ERROR message")
#logger.critical("This is a CRITICAL message")