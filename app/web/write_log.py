from app.web.kafka_logging_handler import KafkaLoggingHandler
import logging


def send_log(value='testvalue'):
    # 获取handler实例
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = KafkaLoggingHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(hdlr=handler)
    #日志发送至kafka
    logger.info(msg=value)