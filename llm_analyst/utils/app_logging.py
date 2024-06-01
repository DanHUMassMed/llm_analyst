import logging

logging.basicConfig(filename='llm_analyst.log', level=logging.DEBUG)
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


logger = logging.getLogger(__name__)

def trace_log(func):
    def wrapper(*args, **kwargs):
        logger.debug("TRACE: Entering %s",func.__name__)
        result = func(*args, **kwargs)
        logger.debug("TRACE: Exiting %s",func.__name__)
        return result
    return wrapper
