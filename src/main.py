#!/usr/bin/env python
import json
import logging
import traceback

import pika

from markets_bridge.utils import (
    SenderFactory,
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
        entities_for_accurate_translation = (
            'PRODUCT_NAME',
            'PRODUCT_DESCRIPTION'
        )
        is_need_accurate_translation = entity_type in entities_for_accurate_translation

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

        sender_cls = SenderFactory.get_sender_cls(entity_type)
        sender_cls.send(entity_id, translation)
    except Exception as e:
        handle_exception(e)
        return
    else:
        logging.info(f'The "{text}" {entity_type.lower()} has been translated into "{translation}"')


# TODO: использовать Sentry
def handle_exception(e: Exception):
    error = f'There was a problem ({e.__class__.__name__}): {e}'
    write_log_entry(error)
    logging.exception(error)
    print(traceback.format_exc())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    connection_parameters = pika.ConnectionParameters(host='localhost', heartbeat=300, blocked_connection_timeout=300)
    with pika.BlockingConnection(connection_parameters) as connection:
        channel = connection.channel()
        channel.queue_declare('translation')
        channel.basic_consume('translation', callback, auto_ack=True)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            pass
