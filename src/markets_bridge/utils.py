from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Literal,
    Optional,
    Type,
)

import requests

import config
from markets_bridge.enums import (
    TranslationTargets,
)


class BaseSender(ABC):
    """Базовый отправитель данных к Markets-Bridge."""

    @classmethod
    @abstractmethod
    def send(cls, entity_id: int, translation: str):
        """Отправляет данные к Markets-Bridge.

        Реализован этот метод, как отправка PATCH запроса для обновления перевода.
        """

    @classmethod
    def _send(cls, url: str, entity_id: int, translation: str, translation_field_name: str):
        headers = get_authorization_headers()
        response = requests.patch(f'{url}{entity_id}/', json={translation_field_name: translation}, headers=headers)

        if response.status_code == 401:
            accesser = Accesser()
            accesser.update_access_token()

            return cls._send(url, entity_id, translation, translation_field_name)

        response.raise_for_status()

        return response

class ProductNameSender(BaseSender):
    """Сущность, обновляющая перевод наименования товаров в Markets-Bridge."""

    @classmethod
    def send(cls, entity_id: int, translation: str):
        return cls._send(
            url=config.products_url,
            entity_id=entity_id,
            translation=translation,
            translation_field_name='translated_name',
        )


class ProductDescriptionSender(BaseSender):
    """Сущность, обновляющая перевод описания товаров в Markets-Bridge."""

    @classmethod
    def send(cls, entity_id: int, translation: str):
        return cls._send(
            url=config.products_url,
            entity_id=entity_id,
            translation=translation,
            translation_field_name='translated_description',
        )


class CategoryNameSender(BaseSender):
    """Сущность, обновляющая перевод наименования категорий в Markets-Bridge."""

    @classmethod
    def send(cls, entity_id: int, translation: str):
        return cls._send(
            url=config.categories_url,
            entity_id=entity_id,
            translation=translation,
            translation_field_name='translated_name',
        )


class CharacteristicNameSender(BaseSender):
    """Сущность, обновляющая перевод наименования характеристик в Markets-Bridge."""

    @classmethod
    def send(cls, entity_id: int, translation: str):
        return cls._send(
            url=config.characteristics_url,
            entity_id=entity_id,
            translation=translation,
            translation_field_name='translated_name',
        )


class CharacteristicValueSender(BaseSender):
    """Сущность, обновляющая перевод значений характеристик в Markets-Bridge."""

    @classmethod
    def send(cls, entity_id: int, translation: str):
        return cls._send(
            url=config.characteristic_values_url,
            entity_id=entity_id,
            translation=translation,
            translation_field_name='translated_value',
        )


class SenderFactory:
    """Фабрика, возвращающая класс отправителя."""

    sender_classes_map = {
        TranslationTargets.PRODUCT_NAME: ProductNameSender,
        TranslationTargets.PRODUCT_DESCRIPTION: ProductDescriptionSender,
        TranslationTargets.CATEGORY_NAME: CategoryNameSender,
        TranslationTargets.CHARACTERISTIC_NAME: CharacteristicNameSender,
        TranslationTargets.CHARACTERISTIC_VALUE: CharacteristicValueSender,
    }

    @classmethod
    def get_sender_cls(
            cls,
            translation_target:
            Literal[
                'PRODUCT_NAME',
                'PRODUCT_DESCRIPTION',
                'CATEGORY_NAME',
                'CHARACTERISTIC_NAME',
                'CHARACTERISTIC_VALUE'
            ]
    ) -> Optional[Type[BaseSender]]:
        try:
            sender_cls = cls.sender_classes_map[translation_target]
        except KeyError as e:
            raise ValueError(f'Не существует типа отправителя для {e}')
        else:
            return sender_cls


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
    return _get_system_variable_value('OPENAI_API_KEY')


def get_openai_expensive_mode() -> bool:
    """Возвращает режим работы OpenAI (дорогой или экономный)."""
    return _get_system_variable_value('IS_OPENAI_EXPENSIVE_MODE').lower() == 'true'


def _get_system_variable_value(variable: str) -> str:
    """Возвращает значение записи из таблицы системных переменных по ключу."""

    headers = get_authorization_headers()
    response = requests.get(f'{config.mb_system_variables_url}{variable}/', headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()

        return _get_system_variable_value(variable)

    response.raise_for_status()
    result = response.json()['value']

    return result


def get_authorization_headers() -> dict:
    accesser = Accesser()
    access_token = accesser.access_token
    headers = {'Authorization': f'Bearer {access_token}'}

    return headers
