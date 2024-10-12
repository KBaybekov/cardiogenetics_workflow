import argparse
import os
import importlib.util

def parse_args():
    # Парсим первый аргумент с путём к конфигу
    initial_args = parse_initial_args()

    # Загружаем и выполняем второй парсер
    parse_cli_args = load_config_parser(initial_args.config_path)
    final_args = parse_cli_args()

    return final_args

def parse_initial_args():
    """
    Парсер для получения пути к конфигу.
    """
    parser = argparse.ArgumentParser(description="Initial argument parser")
    parser.add_argument('-cf', '--config_path', required=True, help="Путь для загрузки конфигурационных файлов")
    args = parser.parse_args()
    return args

def load_config_parser(config_path):
    """
    Импортирует второй парсер из указанного конфиг файла.
    """
    arg_parser = os.path.join(config_path, 'arg_parser.py')
    if not os.path.exists(arg_parser):
        raise FileNotFoundError(f"Парсер не найден: {arg_parser}")

    # Динамически загружаем второй парсер
    spec = importlib.util.spec_from_file_location("config_parser", arg_parser)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    return config_module.parse_cli_args