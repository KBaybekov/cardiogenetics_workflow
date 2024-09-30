import argparse
from src.utils import load_yaml  # Импортируем функцию для загрузки YAML

def parse_cli_args():
    """
    Функция для обработки аргументов командной строки
    """
    arg_descriptions = load_yaml('config/arg_descriptions.yaml')
    default_values = load_yaml('config/default_values.yaml')

    parser = argparse.ArgumentParser(
        description=arg_descriptions['prolog'], 
        epilog=arg_descriptions['epilog']
    )
    
    # Основные аргументы с описаниями из YAML
    parser.add_argument('-i', '--input_dir', required=True, help=arg_descriptions['input_dir'])
    parser.add_argument('-o', '--output_dir', required=True, help=arg_descriptions['output_dir'])
    parser.add_argument('-t', '--threads', default='', help=arg_descriptions['threads'])
    parser.add_argument('-r', '--ref', default='', help=arg_descriptions['ref'])
    parser.add_argument('-p', '--place', required=True, choices=['igor', 'local'], help=arg_descriptions['place'])
    parser.add_argument('-m', '--mode', default='', choices=['WES', 'WGS'], help=arg_descriptions['sequence_mode'])
    parser.add_argument('-s', '--stage', default='', help=arg_descriptions['stage'])
    parser.add_argument('-es', '--exclude_samples', default='', help=arg_descriptions['exclude_samples'])
    parser.add_argument('-is', '--include_samples', default='', help=arg_descriptions['include_samples'])
    parser.add_argument('-f', '--filter_common_variants', default='', help=arg_descriptions['filter_common_variants'])
    parser.add_argument('-frt', '--variant_frequency_threshold', default='', help=arg_descriptions['variant_frequency_threshold'])

    # Парсим аргументы
    args = parser.parse_args()

    # Обработка списков образцов
    list_args = ['exclude_samples', 'include_samples', 'filter_common_variants']
    for arg in list_args:
        value = getattr(args, arg)  # Динамически получаем значение аргумента
        setattr(args, arg, value.split(',') if value else [])

    # Присваивание значений по умолчанию в случае отсутствия аргумента в CMD
    for arg, default_value in default_values[args.place].items():
        if getattr(args, arg) == '':
            setattr(args, arg, default_value)

    return args