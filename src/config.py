import os

from dotenv import (
    load_dotenv,
)


load_dotenv()


# Markets-Bridge
mb_domain = os.getenv('MB_DOMAIN')

if not mb_domain:
    raise ValueError('Не задан домен Markets-Bridge.')

products_url = f'{mb_domain}api/v1/provider/products/'
categories_url = f'{mb_domain}api/v1/provider/categories/'
characteristics_url = f'{mb_domain}api/v1/provider/characteristics/'
characteristic_values_url = f'{mb_domain}api/v1/provider/characteristic_values/'
untranslated_products_url = f'{mb_domain}api/v1/provider/products/random_untranslated/'
untranslated_category_url = f'{mb_domain}api/v1/provider/categories/random_untranslated/'
untranslated_characteristic_url = f'{mb_domain}api/v1/provider/characteristics/random_untranslated/'
untranslated_value_url = f'{mb_domain}api/v1/provider/characteristic_values/random_untranslated/'


