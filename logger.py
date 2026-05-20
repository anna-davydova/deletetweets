import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler(
    filename="log_file.log",
    mode="a",
    encoding="utf-8"
)
formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d - [%(levelname)s] - %(message)s',
                              datefmt='%d.%m.%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)