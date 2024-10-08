import logging

class NoHTTPFilter(logging.Filter):
    def filter(self, record):
        return 'HTTP' not in record.getMessage()

logging.basicConfig(filename='bot.log',
                    filemode='a',
                    format='%(asctime)s - %(message)s',
                    datefmt='%m-%d %H:%M',
                    level=logging.WARNING)

logger = logging.getLogger()
logger.addFilter(NoHTTPFilter())
