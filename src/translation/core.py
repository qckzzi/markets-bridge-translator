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

from markets_bridge.utils import (
    get_openai_api_key,
)
from translation import (
    promts,
)


_last_accurate_translate_time = None


def accurate_translate(text: str, translation_object_type: str):
    """Translates text using unique promts for each translation object type.

    Example:
        translate('iPad 9. Nesil 64 GB', 'PRODUCT')
    """

    global _last_accurate_translate_time

    if not _last_accurate_translate_time:
        _last_accurate_translate_time = datetime.now()
    else:
        different = 20 - (datetime.now() - _last_accurate_translate_time).total_seconds()
        if different > 0:
            time.sleep(different + 1)

    _last_accurate_translate_time = datetime.now()

    message = {'role': 'user', 'content': f'Untranslated text: "{text}"'}
    messages = getattr(promts, translation_object_type)[:]
    messages.append(message)

    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )

    return completion.choices[0].message.content


def simple_translate(text: str):
    try:
        translate = translators.translate_text(text, translator='alibaba', from_language='tr', to_language='ru')
    except Exception:
        return _simple_translate_with_random_translator(text)

    return translate


def _simple_translate_with_random_translator(text: str):
    try:
        translate = translators.translate_text(
            text,
            translator=random.choice(translators_pool),
            from_language='tr',
            to_language='ru'
        )
    except Exception:
        return _simple_translate_with_random_translator(text)

    return translate