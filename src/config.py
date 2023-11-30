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
mb_login = os.getenv('MB_LOGIN')
mb_password = os.getenv('MB_PASSWORD')

if not (mb_login and mb_password):
    raise ValueError('MB_LOGIN and MB_PASSWORD not set for Markets-Bridge authentication')

mb_token_url = mb_domain + 'api/token/'
mb_token_refresh_url = mb_token_url + 'refresh/'
mb_system_environments_url = mb_domain + 'api/v1/common/system_environments/'
mb_logs_url = mb_domain + 'api/v1/common/logs/'

is_simple_gpt = os.getenv('IS_SIMPLE_GPT').lower() == 'true'
