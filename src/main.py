#!/usr/bin/env python
import argparse
import threading

from category_translate import (
    translate_categories,
)
from characteristic_translate import (
    translate_characteristics,
)
from characteristic_value_translate import (
    translate_characteristic_values,
)
from product_translate import (
    translate_products,
)


def main():
    # TODO: Переделать под ООП
    translate_products()
    translate_characteristics()
    translate_characteristic_values()
    translate_categories()


if __name__ == '__main__':
    # TODO: Слишком неэффективно использовать потоки в данном случае, необходимо переписать сервис на Fast Api
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--num_threads',
        type=int,
        default=1,
        help='Количество потоков',
    )
    args = parser.parse_args()

    MAX_THREADS_NUMBER = 20
    if args.num_threads > MAX_THREADS_NUMBER:
        args.num_threads = MAX_THREADS_NUMBER

    threads = []

    for _ in range(args.num_threads):
        t = threading.Thread(target=main)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
