#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import os
from jinja2 import Environment, FileSystemLoader

# ---------- ПУТИ ----------
# Эти пути заданы относительно расположения generate.py.
# Предположим, что generate.py лежит в tools/generator/
# и protocol.yaml лежит в protocol/ (на уровень выше tools/generator/..)
# Можно задать абсолютные или относительные пути.
YAML_FILE = "../../protocol/protocol.yaml"          # путь к YAML
OUTPUT_PY = "../../app_test_stnd/generated_protocol.py"
OUTPUT_C_H = "../../testUART/Core/Inc/protocol.h"
OUTPUT_C_C = "../../testUART/Core/Src/protocol.c"
# ----------------------------------------------------


def load_protocol(yaml_path):
    """
    Загружает данные из YAML-файла.
    Возвращает словарь с ключами:
        - commands: список команд
        - error_codes: словарь {имя_ошибки: код} (может отсутствовать)
    """
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        # Если data — словарь и содержит ключ 'commands', используем его
        if isinstance(data, dict) and 'commands' in data:
            result = {
                'commands': data['commands'],
                'error_codes': data.get('error_codes', {})  # если нет, то пустой словарь
            }
            return result
        # Если data — список, то это список команд, а error_codes нет
        elif isinstance(data, list):
            return {
                'commands': data,
                'error_codes': {}
            }
        else:
            raise ValueError("YAML должен содержать ключ 'commands' или быть списком команд.")


def generate_python(protocol_data, output_path):
    """
    Генерирует Python-модуль из данных протокола.
    protocol_data — словарь с ключами 'commands' и 'error_codes'.
    """
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template('protocol.py.j2')
    rendered = template.render(
        commands=protocol_data['commands'],
        error_codes=protocol_data.get('error_codes', {})
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    print(f"Python-модуль сгенерирован: {output_path}")


def generate_c(protocol_data, header_path, source_path):
    """
    Генерирует C-заголовок и реализацию из данных протокола.
    protocol_data — словарь с ключами 'commands' и 'error_codes'.
    """
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    # Заголовок
    template_h = env.get_template('protocol.h.j2')
    rendered_h = template_h.render(
        commands=protocol_data['commands'],
        error_codes=protocol_data.get('error_codes', {})
    )
    os.makedirs(os.path.dirname(header_path), exist_ok=True)
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(rendered_h)
    print(f"C-заголовок сгенерирован: {header_path}")

    # Реализация
    template_c = env.get_template('protocol.c.j2')
    rendered_c = template_c.render(
        commands=protocol_data['commands'],
        error_codes=protocol_data.get('error_codes', {})
    )
    os.makedirs(os.path.dirname(source_path), exist_ok=True)
    with open(source_path, 'w', encoding='utf-8') as f:
        f.write(rendered_c)
    print(f"C-реализация сгенерирована: {source_path}")


if __name__ == '__main__':
    protocol_data = load_protocol(YAML_FILE)
    generate_python(protocol_data, OUTPUT_PY)
    generate_c(protocol_data, OUTPUT_C_H, OUTPUT_C_C)
    print("Генерация завершена.")