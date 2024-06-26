"""
This module configures logging settings for various libraries and provides a decorator
function to trace the entry and exit points of other functions.
"""

import logging

logging.basicConfig(level=logging.DEBUG)

# The below provide lots of DEBUG logging that is not desired
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("hpack.hpack").setLevel(logging.WARNING)
logging.getLogger("hpack.table").setLevel(logging.WARNING)
logging.getLogger("langchain_community.utils.math").setLevel(logging.WARNING)
logging.getLogger("fontTools.ttLib.ttFont").setLevel(logging.WARNING)
logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


def trace_log(func):
    def wrapper(*args, **kwargs):
        logger.debug("TRACE: Entering %s", func.__name__)
        result = func(*args, **kwargs)
        logger.debug("TRACE: Exiting %s", func.__name__)
        return result

    return wrapper
