import time
from datetime import (
    datetime,
)

import translators
from openai import (
    OpenAI,
)

import config
from translation import (
    promts,
)


_client = None
_last_accurate_translate_time = None


def accurate_translate(text: str, translation_object_type: str):
    """Translates text using unique promts for each translation object type.

    Example:
        translate('iPad 9. Nesil 64 GB', 'PRODUCT')
    """

    global _client

    if not _client:
        _client = OpenAI(api_key=config.openai_api_key)

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
    completion = _client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )

    return completion.choices[0].message.content


def simple_translate(text: str):
    translate = translators.translate_text(text, translator='deepl', from_language='tr', to_language='ru')

    return translate

