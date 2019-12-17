import logging
import ssl
from kafka import KafkaProducer
from kafka.errors import KafkaError
from numpy import unicode


context = ssl.create_default_context()
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations("app/web/ca-cert")


class KafkaLoggingHandler(logging.Handler):

    def __init__(self, **kwargs):
        logging.Handler.__init__(self)
        self.kafka_topic_name = "topic1"
        self.producer = KafkaProducer(bootstrap_servers='118.31.64.108:9093',
                                      sasl_mechanism="PLAIN",
                                      ssl_context=context,
                                      security_protocol='SASL_SSL',
                                      api_version=(0, 10),
                                      retries=5,
                                      sasl_plain_username='alikafka_post-cn-v641ftl7v00i',
                                      sasl_plain_password='tTgG0QePVLXV2w9h7aqIXW4yet8m7sjJ'
                                      )
        # partitions = self.producer.partitions_for('topic1')

    def emit(self, record):
        # 忽略kafka的日志，以免导致无限递归。
        if 'kafka' in record.name:
            return

        try:
            # 格式化日志并指定编码为utf-8
            msg = self.format(record)
            if isinstance(msg, unicode):
                msg = msg.encode("utf-8")

            # kafka生产者，发送消息到broker。
            future = self.producer.send(self.kafka_topic_name, msg)
            future.get()
            print('send message succeed.')
        except KafkaError as e:
            print('send message failed.')
            print(e)
        except Exception:
            self.handleError(record)

    def close(self):
        # self.producer.stop()
        logging.Handler.close(self)


