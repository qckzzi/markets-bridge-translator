import random
import time
from datetime import (
    datetime,
)

import translators
from openai import (
    OpenAI,
)
from translators import (
    translators_pool,
)

import config
from markets_bridge.utils import (
    get_openai_api_key,
)
from translation import (
    promts,
)


# TODO: Написать класс Translator
_last_accurate_translate_time = None
_translation_timeout = 30.0


def accurate_translate(text: str, translation_object_type: str):
    """Translates text using unique promts for each translation object type.

    Example:
        translate('iPad 9. Nesil 64 GB', 'PRODUCT')
    """

    if config.is_simple_gpt:
        wait_for_translation()

    message = {'role': 'user', 'content': f'Untranslated text: "{text}"'}
    messages = getattr(promts, translation_object_type)[:]
    messages.append(message)

    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key, timeout=_translation_timeout)

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo' if config.is_simple_gpt else 'gpt-4',
        messages=messages,
        temperature=0,
        timeout=_translation_timeout,
    )

    return completion.choices[0].message.content


# FIXME: DRY
def simple_translate(text: str):
    try:
        translate = translators.translate_text(
            text,
            translator='alibaba',
            from_language='tr',
            to_language='ru',
            timeout=_translation_timeout,
        )
    except Exception:
        return _simple_translate_with_random_translator(text)

    return translate


def _simple_translate_with_random_translator(text: str):
    try:
        translate = translators.translate_text(
            text,
            translator=random.choice(translators_pool),
            from_language='tr',
            to_language='ru',
            timeout=_translation_timeout,
        )
    except Exception:
        return _simple_translate_with_random_translator(text)

    return translate


def wait_for_translation():
    global _last_accurate_translate_time

    if not _last_accurate_translate_time:
        _last_accurate_translate_time = datetime.now()
    else:
        different = 20 - (datetime.now() - _last_accurate_translate_time).total_seconds()
        if different > 0:
            time.sleep(different + 1)

    _last_accurate_translate_time = datetime.now()
