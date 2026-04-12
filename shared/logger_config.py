import logging
import time

class LoggerFactory:
    @staticmethod
    def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.handlers:
            handler = logging.StreamHandler()
            log_format = '%(asctime)s\t%(levelname)s\t%(message)s'
            date_format = '%Y-%m-%dT%H:%M:%SZ'
            
            formatter = logging.Formatter(log_format, date_format)

            formatter.converter = time.gmtime 

            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = False

        return logger