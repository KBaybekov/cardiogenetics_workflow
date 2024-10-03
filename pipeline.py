from src import *
from src.utils import load_yaml

def main():
    # Парсинг аргументов командной строки
    args = parse_cli_args()
    # Инициализация пайплайна
    pipeline = PipelineManager(args)
    # Загрузка конфигурации машины
    pipeline.load_machine_vars(config_path=args['configs'], machine=args['machine'])
    #Запуск пайплайна
    pipeline.run_pipeline()

if __name__ == '__main__':
    main()