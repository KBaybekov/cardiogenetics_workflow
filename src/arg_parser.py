import argparse
import os
from src.utils import load_yaml  # Импортируем функцию для загрузки YAML

def parse_cli_args():
    """
    Функция для обработки аргументов командной строки
    """
    configs = os.path.dirname(os.path.realpath(__file__)).replace('src', 'config')
    arg_descriptions = load_yaml(f'{configs}arg_descriptions.yaml', critical=True)
        
    parser = argparse.ArgumentParser(
        description=arg_descriptions['prolog'], 
        epilog=arg_descriptions['epilog']
    )
    
    # Основные аргументы с описаниями из YAML
    parser.add_argument('-i', '--input_dir', required=True, type=str, help=arg_descriptions['input_dir'])
    parser.add_argument('-o', '--output_dir', required=True, type=str, help=arg_descriptions['output_dir'])
    parser.add_argument('-t', '--threads', default='', type=str, help=arg_descriptions['threads'])
    parser.add_argument('-r', '--ref_fasta', default='', type=str, help=arg_descriptions['ref_fasta'])
    parser.add_argument('-mc', '--machine', required=True, type=str, help=arg_descriptions['machine'])
    parser.add_argument('-sm', '--seq_mode', default='', type=str, choices=['WES', 'WGS'], help=arg_descriptions['sequence_mode'])
    parser.add_argument('-m', '--modules', default='', type=str, help=arg_descriptions['modules'])
    parser.add_argument('-es', '--exclude_samples', default='', type=str, help=arg_descriptions['exclude_samples'])
    parser.add_argument('-is', '--include_samples', default='', type=str, help=arg_descriptions['include_samples'])
    parser.add_argument('-f', '--filter_common_variants', default='', type=str, help=arg_descriptions['filter_common_variants'])
    parser.add_argument('-vf', '--variant_filters', default='', type=str, help=arg_descriptions['variant_filters'])
    parser.add_argument('-frt', '--variant_frequency_threshold', default='', type=str, help=arg_descriptions['variant_frequency_threshold'])
    parser.add_argument('-dm', '--demo', default='', type=str, help=arg_descriptions['demo'])
    parser.add_argument('-cf', '--project_path', default='', type=str, help=arg_descriptions['project_path'])
    parser.add_argument('-cr', '--cravat_annotators', default='', type=str, help=arg_descriptions['cravat_annotators'])
    parser.add_argument('-s', '--subfolders', default=False, type=str, help=arg_descriptions['subfolders'])

    # Парсим аргументы
    args = parser.parse_args()

    # Обработка списков образцов
    list_args = ['exclude_samples', 'include_samples', 'filter_common_variants']
    for arg in list_args:
        value = getattr(args, arg)  # Динамически получаем значение аргумента
        setattr(args, arg, value.split(',') if value else [])

    if args.cravat_annotators != '':
        args.cravat_annotators = ' '.join(args.cravat_annotators.split(','))

    if args.modules != '':
        args.modules = args.modules.split(',')

    # Загрузка значений по умолчанию
    default_values = load_yaml(f"{configs}/default_values.yaml",
                               critical=True)

    # Присваивание значений по умолчанию в случае отсутствия аргумента в CMD
    for arg, default_value in default_values.items():
        if getattr(args, arg) == '':
            setattr(args, arg, default_value)
    #Добавим кавычки в variant_filters
    args['variant_filters'] = f'"{args["variant_filters"]}"'

    # Преобразуем Namespace в словарь
    args = vars(args)  # Преобразуем объект Namespace в словарь

    return args