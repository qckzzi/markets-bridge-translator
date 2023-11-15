#!/usr/bin/env python
import json
import logging

import pika

from markets_bridge.utils import (
    Sender,
    write_log_entry,
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
                error = f'An error has occurred. A simple translation is used. Error: {e}'
                write_log_entry(error)
                logging.error(error)
                translation = simple_translate(text)
        else:
            translation = simple_translate(text)

        sending_function = Sender.get_sending_method_for_entity_type(entity_type)
        sending_function(entity_id, translation)

    except KeyError as e:
        error = f'Body validation error: {e}'
        write_log_entry(error)
        logging.error(error)
        return
    except Exception as e:
        error = f'There was a problem: {e}'
        write_log_entry(error)
        logging.exception(error)
        return
    else:
        logging.info(f'The "{text}" {entity_type.lower()} has been translated into "{translation}"')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    connection_parameters = pika.ConnectionParameters(host='localhost', heartbeat=300, blocked_connection_timeout=300)
    with pika.BlockingConnection(connection_parameters) as connection:
        channel = connection.channel()
        channel.queue_declare('translation')
        channel.basic_consume('translation', callback, auto_ack=True)
        channel.start_consuming()
