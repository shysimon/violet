import ssl
import socket
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import redis

def save_to_redis(key='test'):
    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    # context.check_hostname = True
    context.load_verify_locations("ca-cert")


    consumer = KafkaConsumer(bootstrap_servers='118.31.64.108:9093',
                    group_id='group1',
                    sasl_mechanism="PLAIN",
                    ssl_context=context,
                    security_protocol='SASL_SSL',
                    api_version = (0,10),
                    sasl_plain_username='alikafka_post-cn-v641ftl7v00i',
                    sasl_plain_password='tTgG0QePVLXV2w9h7aqIXW4yet8m7sjJ')


    print('consumer start to consuming...')
    r = redis.Redis(host="r-bp1t83j1bcl1en2trzpd.redis.rds.aliyuncs.com",port=6379, password= "123456Dtr", db=0)
    consumer.subscribe(('topic1', ))
    for message in consumer:
        print(message.topic, message.offset, message.key, message.value, message.partition)
        r.sadd(key, message.value)