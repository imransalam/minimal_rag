"""
This module provides a simple logging utility for recording informational and error messages
to both the console and a log file. 

- Log File: Logs are written to `app.log` in the current directory.
- Log Levels: Supports 'info' and 'error' log levels.
"""

import logging
import datetime

# Configure the logging system
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def _log(txt: str, 
         format: str = 'info') -> None:
    """
    Log a message to both the console and the log file, with a timestamp.

    Parameters
    ----------
    txt : str
        The message to be logged.
    format : str, optional
        The logging level of the message ('info' or 'error'). Defaults to 'info'.

    Returns
    -------
    None
    """
    # Create the log message with a timestamp
    log_message: str = f"{txt} | {datetime.datetime.now()}"
    
    # Print the log message to the console
    print(log_message)
    
    # Write the log message to the file
    if format.lower() == 'info':
        logging.info(log_message)
    elif format.lower() == 'error':
        logging.error(log_message)
    else:
        raise ValueError("Invalid log format. Use 'info' or 'error'.")