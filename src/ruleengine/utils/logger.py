import logging
import sys


class FixedLengthFileNameFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', fixed_length=16):
        super().__init__(fmt, datefmt, style)
        self.fixed_length = fixed_length

    def format(self, record):
        filename = record.filename
        if len(filename) > self.fixed_length:
            filename = filename[:self.fixed_length - 3] + "..."  # trunc file name
        else:
            filename = filename.rjust(self.fixed_length)
        record.filename = filename
        return super().format(record)


LOGGING_FORMAT = "[%(levelname)s] [%(asctime)s] [%(filename)s, line: %(lineno)04d]: %(message)s"
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
handler.setFormatter(FixedLengthFileNameFormatter(fmt=LOGGING_FORMAT))
logger.addHandler(handler)
logger.propagate = False
