#!/usr/bin/env python
import json
import logging

import pika

from markets_bridge.services import (
    Sender,
)
from translation.core import (
    accurate_translate,
    simple_translate,
)


# TODO: Декомпозировать
def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        entity_id = message['id']
        text = message['text']
        entity_type = message['type']

        logging.info(f'The "{text}" {entity_type.lower()} was received for translation.')

        is_need_accurate_translation = entity_type == 'PRODUCT'

        if is_need_accurate_translation:
            try:
                translation = accurate_translate(text, entity_type)
            except Exception as e:
                logging.error(f'An error has occurred. A simple translation is used. Error: {e}')
                translation = simple_translate(text)
        else:
            translation = simple_translate(text)

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
