import random
import sys

import pika
from django.conf import settings
from fabrique.logger import logger
from kafka import KafkaConsumer


class BaseSync:
    """
    Базовый класс для работы с RabbitMQ.
    Устанавливается подключение, создаются queue и exchange, используемые в приложении.
    """

    connection_mq = None
    mq_channel = None
    consumer_kafka = None

    def connect_mq(self, heartbeat=90):
        parameters = []
        credentials = pika.PlainCredentials(
            settings.RABBITMQ["USER"], settings.RABBITMQ["PASSWORD"]
        )
        for host in settings.RABBITMQ["HOSTS"].split(","):
            parameters.append(
                pika.ConnectionParameters(
                    host=host.strip(),
                    virtual_host=settings.RABBITMQ["VHOST"],
                    connection_attempts=5,
                    retry_delay=1,
                    credentials=credentials,
                    heartbeat=heartbeat,
                    blocked_connection_timeout=heartbeat,
                )
            )

        self.connection_mq = pika.BlockingConnection(random.choice(parameters))
        self.mq_channel = self.connection_mq.channel()
        self.mq_channel.exchange_declare(
            exchange="enps", durable=True, auto_delete=False
        )

        self.mq_channel.queue_declare(queue="enps__poll_notifications", durable=True)
        self.mq_channel.queue_bind("enps__poll_notifications", "enps")
        self.mq_channel.queue_declare(
            queue="enps__poll_push_notifications", durable=True
        )
        self.mq_channel.queue_bind("enps__poll_push_notifications", "enps")

        self.mq_channel.queue_declare(queue="enps__async_tasks", durable=True)
        self.mq_channel.queue_bind("enps__async_tasks", "enps")

    def connect_kafka(self):
        self.consumer_kafka = KafkaConsumer(
            settings.KAFKA["TOPIC"],
            bootstrap_servers=settings.KAFKA["BOOTSTRAP_SERVERS"],
            client_id="feedback-receipt-watcher",
            group_id="feedback-receipt-watcher",
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="GSSAPI",
            api_version=(0, 10, 1),
            retry_backoff_ms=500,
            fetch_max_wait_ms=2000,
            auto_commit_interval_ms=10000,
            max_poll_records=500,
            max_poll_interval_ms=300000,
            session_timeout_ms=15000,
            heartbeat_interval_ms=6000,
            auto_offset_reset="smallest",
            enable_auto_commit=True,
        )

    def debug_logging(self):
        logger.info(
            event="debug_logging",
            message="Set logging...",
        )
        import logging

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)
        logging.basicConfig(level=logging.DEBUG)
