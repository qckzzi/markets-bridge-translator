[![Python 3.12](https://img.shields.io/badge/python-3.12-green.svg)](https://www.python.org/downloads/release/python-3120/)
# markets-bridge-translator
## Описание
Данный сервис является переводчиком parsed данных. Является непосредственной частью системы
Markets-Bridge.

Его задачи:
1. Получает непереведенный текст и запись, у которой нужно его перевести;
2. Переводит текст;
3. Обновляет данные, обращаясь по API к [Markets-Bridge](https://github.com/qckzzi/markets-bridge-drf-app).

Перевод работает в двух режимах:
* Качественный (с помощью OpenAI GPT);
* Быстрый (с помощью одного из переводчиков, указанных в библиотеке [translators](https://pypi.org/project/translators/)).

## Установка
### Конфигурация системы
Для функционирования системы необходимы:
- Запущенный instance [Markets-Bridge](https://github.com/qckzzi/markets-bridge-drf-app);
- [RabbitMQ server](https://www.rabbitmq.com/download.html);
- Python, поддерживаемой версии (разработка велась на 3.12.0).

### Установка проекта
Клонируем проект в необходимую директорию:
```shell
git clone git@github.com:qckzzi/markets-bridge-translator.git
```
```shell
cd markets-bridge-translator
```
Создадим виртуальное окружение:
```shell
python3 -m venv venv
```
(или любым другим удобным способом)

Активируем его:
```shell
. venv/bin/activate
```
Установим зависимости:

(для разработки)
```shell
pip install -r DEV_REQUIREMENTS.txt
```
(для деплоя)
```shell
pip install -r REQUIREMENTS.txt
```
В корневой директории проекта необходимо скопировать файл ".env.example", переименовать
его в ".env" и заполнить в соответствии с вашей системой.

Запуск сервиса:
```shell
python3 src/main.py
```
## Разработка

Для внесения изменений в кодовую базу необходимо инициализировать pre-commit git hook.
Это можно сделать командой в терминале, находясь в директории проекта:
```shell
pre-commit install
```
Это необходимо для поддержания 
единого кодстайла в проекте. При каждом коммите будет запущен форматировщик.