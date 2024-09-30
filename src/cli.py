import argparse

def parse_cli_args():
    """
    Функция для обработки аргументов командной строки.
    Возвращает объект с параметрами, которые используются в пайплайне.
    """
    parser = argparse.ArgumentParser(description="Bioinformatics Pipeline CLI")
    
    # Основные аргументы
    parser.add_argument('-f', '--folder', required=True, help="Папка с исходными файлами")
    parser.add_argument('-t', '--threads', required=True, type=int, help="Количество потоков для анализа")
    parser.add_argument('-r', '--ref', required=True, help="Путь к референсному файлу (FASTA)")
    parser.add_argument('-p', '--place', required=True, choices=['igor', 'local'], help="Место запуска пайплайна")
    parser.add_argument('-m', '--mode', required=True, choices=['WES', 'WGS'], help="Тип секвенирования (WES или WGS)")
    parser.add_argument('-s', '--stage', default='all', help="Этап пайплайна, который нужно запустить (по умолчанию: all)")
    parser.add_argument('--exclude_samples', default='', help="Список образцов для исключения (разделённые запятой)")
    parser.add_argument('--include_samples', default='', help="Список образцов для включения (разделённые запятой)")

    # Парсим аргументы
    args = parser.parse_args()

    # Обработка списков для include/exclude samples
    args.include_samples = args.include_samples.split(',') if args.include_samples else []
    args.exclude_samples = args.exclude_samples.split(',') if args.exclude_samples else []

    return args
