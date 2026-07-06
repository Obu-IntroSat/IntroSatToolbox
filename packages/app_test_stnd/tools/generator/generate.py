#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import os
from jinja2 import Environment, FileSystemLoader

# ---------- ПУТИ ----------
YAML_FILE = "../../protocol/protocol.yaml"
OUTPUT_PY = "../../app_test_stnd/generated_protocol.py"
OUTPUT_C_H = "../../firmware/inc/protocol.h"
OUTPUT_C_C = "../../firmware/src/protocol.c"
# ----------------------------------------------------


def load_protocol(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_python(protocol_data, output_path):
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template('protocol.py.j2')
    rendered = template.render(commands=protocol_data['commands'])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    print(f"Python-модуль сгенерирован: {output_path}")


def generate_c(protocol_data, header_path, source_path):
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    # Генерируем заголовок
    template_h = env.get_template('protocol.h.j2')
    rendered_h = template_h.render(commands=protocol_data['commands'])
    os.makedirs(os.path.dirname(header_path), exist_ok=True)
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(rendered_h)
    # Генерируем реализацию
    template_c = env.get_template('protocol.c.j2')
    rendered_c = template_c.render(commands=protocol_data['commands'])
    os.makedirs(os.path.dirname(source_path), exist_ok=True)
    with open(source_path, 'w', encoding='utf-8') as f:
        f.write(rendered_c)
    print(f"C-заголовок сгенерирован: {header_path}")
    print(f"C-реализация сгенерирована: {source_path}")


if __name__ == '__main__':
    protocol = load_protocol(YAML_FILE)
    generate_python(protocol, OUTPUT_PY)
    generate_c(protocol, OUTPUT_C_H, OUTPUT_C_C)
    print("Генерация завершена.")
