import time
import json
import logging
import datetime

import pika
from sqlalchemy import select

from .config import RABBITMQ_URL, OUTBOX_POLL_INTERVAL
from .database import SessionLocal
from .models import MessageOutbox
from .rabbitmq import get_rabbitmq_connection

# ─────────────────────────────────── Setup Logging ─────────────────────────────────────────
logger = logging.getLogger("outbox_publisher")
logging.basicConfig(level=logging.INFO)


def publish_outbox_messages():
    """
    Polls the message_outbox table for unsent messages, publishes them to RabbitMQ,
    and updates their sent_at and error fields accordingly.
    """
    # Establish RabbitMQ connection
    try:
        conn = get_rabbitmq_connection()
        channel = conn.channel()
        # Ensure publisher confirms when possible
        channel.confirm_delivery()
        logger.info("Connected to RabbitMQ for outbox publishing.")
    except Exception as e:
        logger.exception("Failed to connect to RabbitMQ: %s", e)
        return

    while True:
        session = SessionLocal()
        try:
            # Fetch unsent messages
            stmt = select(MessageOutbox).where(MessageOutbox.sent_at == None)
            msgs = session.execute(stmt).scalars().all()
            for msg in msgs:
                try:
                    body = json.dumps(msg.payload)
                    properties = pika.BasicProperties(delivery_mode=2)  # persistent
                    channel.basic_publish(
                        exchange=msg.exchange or '',
                        routing_key=msg.routing_key,
                        body=body,
                        properties=properties
                    )
                    msg.sent_at = datetime.datetime.utcnow()
                    msg.error = None
                    logger.info(f"Published outbox id={msg.id} to '{msg.routing_key}'")
                except Exception as e:
                    msg.error = str(e)
                    logger.exception(f"Failed to publish outbox id={msg.id}: {e}")
                finally:
                    session.add(msg)
                    session.commit()
        except Exception as e:
            logger.exception("Error polling outbox: %s", e)
            session.rollback()
        finally:
            session.close()

        time.sleep(OUTBOX_POLL_INTERVAL)


if __name__ == "__main__":
    publish_outbox_messages()
