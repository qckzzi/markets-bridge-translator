import os

from dotenv import (
    load_dotenv,
)


load_dotenv()


# Markets-Bridge
mb_domain = os.getenv('MB_DOMAIN')

if not mb_domain:
    raise ValueError('MB_DOMAIN not set')

products_url = f'{mb_domain}api/v1/provider/products/'
categories_url = f'{mb_domain}api/v1/provider/categories/'
characteristics_url = f'{mb_domain}api/v1/provider/characteristics/'
characteristic_values_url = f'{mb_domain}api/v1/provider/characteristic_values/'


# OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    raise ValueError('OPENAI_API_KEY not set')
