#!/usr/bin/env python
import json
import logging
import time

import pika

from markets_bridge.services import (
    Sender,
)
from translation.core import (
    translate,
)


def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        entity_id = message['id']
        text = message['text']
        entity_type = message['type']

        logging.info(f'The "{text}" {entity_type.lower()} was received for translation.')
        translation = translate(text, entity_type)

        sending_function = Sender.get_sending_method_for_entity_type(entity_type)
        sending_function(entity_id, translation)

    except KeyError as e:
        logging.exception(f'Body validation error: {e}')
        return
    except Exception as e:
        logging.exception(f'There was a problem: {e}')
        return
    else:
        logging.info(f'The "{text}" product has been translated into "{translation}"')

    # Translator usage limit (can send 3 requests per minute)
    time.sleep(20)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    connection_parameters = pika.ConnectionParameters(host='localhost', heartbeat=300, blocked_connection_timeout=300)
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.queue_declare('translation')
    channel.basic_consume('translation', callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.close()
        connection.close()
