import requests
from requests import (
    Response,
)

import config
from markets_bridge.enums import (
    EntityType,
)


class Sender:
    """Отправитель данных к сервису Markets-Bridge."""

    @classmethod
    def get_sending_method_for_entity_type(cls, entity_type: str):
        method_for_entity_type_map = {
            EntityType.PRODUCT: cls.send_product,
            EntityType.CATEGORY: cls.send_category,
            EntityType.CHARACTERISTIC: cls.send_characteristic,
            EntityType.CHARACTERISTIC_VALUE: cls.send_characteristic_value,
        }

        return method_for_entity_type_map[entity_type]

    # TODO: DRY
    @classmethod
    def send_product(cls, product_id: int, translation: str) -> Response:
        url = config.products_url
        headers = get_authorization_headers()
        response = requests.patch(f'{url}{product_id}/', json={'translated_name': translation}, headers=headers)

        if response.status_code == 401:
            accesser = Accesser()
            accesser.update_access_token()

            return cls.send_product(product_id, translation)

        response.raise_for_status()

        return response

    @classmethod
    def send_category(cls, category_id: int, translation: str) -> Response:
        url = config.categories_url
        headers = get_authorization_headers()
        response = requests.patch(f'{url}{category_id}/', json={'translated_name': translation}, headers=headers)

        if response.status_code == 401:
            accesser = Accesser()
            accesser.update_access_token()

            return cls.send_category(category_id, translation)

        response.raise_for_status()

        return response

    @classmethod
    def send_characteristic(cls, characteristic_id: int, translation: str) -> Response:
        url = config.characteristics_url
        headers = get_authorization_headers()
        response = requests.patch(f'{url}{characteristic_id}/', json={'translated_name': translation}, headers=headers)

        if response.status_code == 401:
            accesser = Accesser()
            accesser.update_access_token()

            return cls.send_characteristic(characteristic_id, translation)

        response.raise_for_status()

        return response

    @classmethod
    def send_characteristic_value(cls, value_id: int, translation: str) -> Response:
        url = config.characteristic_values_url
        headers = get_authorization_headers()
        response = requests.patch(f'{url}{value_id}/', json={'translated_value': translation}, headers=headers)

        if response.status_code == 401:
            accesser = Accesser()
            accesser.update_access_token()

            return cls.send_characteristic_value(value_id, translation)

        response.raise_for_status()

        return response


class Singleton:
    _instance = None
    _initialized = False

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance


class Accesser(Singleton):
    """Получатель доступа к сервису Markets-Bridge.

    При первичном получении токена доступа генерируется JWT. При истечении access токена необходимо вызывать
    update_access_token(). В случае, если refresh токен умер, вызывается метод update_jwt().
    """

    def __init__(self):
        if not self._initialized:
            self._refresh_token = None
            self._access_token = None

            self._initialized = True

    @property
    def access_token(self) -> str:
        if not self._access_token:
            self.update_jwt()

        return self._access_token

    def update_jwt(self):
        login_data = {
            'username': config.mb_login,
            'password': config.mb_password
        }

        response = requests.post(config.mb_token_url, data=login_data)
        response.raise_for_status()
        token_data = response.json()
        self._access_token = token_data['access']
        self._refresh_token = token_data['refresh']

    def update_access_token(self):
        body = {'refresh': self._refresh_token}

        response = requests.post(config.mb_token_refresh_url, json=body)

        if response.status_code == 401:
            self.update_jwt()
            self.update_access_token()

            return

        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data['access']


def write_log_entry(message: str):
    """Создает записи логов в сервисе Markets-Bridge."""

    body = {'service_name': 'Translator', 'entry': message}
    headers = get_authorization_headers()
    response = requests.post(config.mb_logs_url, json=body, headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()

        return write_log_entry(message)

    response.raise_for_status()


def get_openai_api_key() -> str:
    """Возвращает OpenAI API ключ из сервиса Markets-Bridge."""
    return _get_system_environment_value('OPENAI_API_KEY')


def get_openai_expensive_mode() -> bool:
    """Возвращает режим работы OpenAI (дорогой или экономный)."""
    return _get_system_environment_value('IS_OPENAI_EXPENSIVE_MODE').lower() == 'true'


def _get_system_environment_value(environment: str) -> str:
    """Возвращает значение записи из таблицы системных переменных по ключу."""

    headers = get_authorization_headers()
    response = requests.get(f'{config.mb_system_environments_url}{environment}/', headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()

        return _get_system_environment_value(environment)

    response.raise_for_status()
    result = response.json()['value']

    return result


def get_authorization_headers() -> dict:
    accesser = Accesser()
    access_token = accesser.access_token
    headers = {'Authorization': f'Bearer {access_token}'}

    return headers
