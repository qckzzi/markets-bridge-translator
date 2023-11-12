from openai import (
    OpenAI,
)

import config
from translation import (
    promts,
)


_client = OpenAI(api_key=config.openai_api_key)


def translate(text: str, translation_object_type: str):
    """Translates text using unique promts for each translation object type.

    Example:
        translate('iPad 9. Nesil 64 GB', 'PRODUCT')
    """

    message = {'role': 'user', 'content': f'Untranslated text: "{text}"'}
    messages = getattr(promts, translation_object_type)[:]
    messages.append(message)
    completion = _client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )

    return completion.choices[0].message.content
