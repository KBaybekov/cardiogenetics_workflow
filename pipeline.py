from src import *


def main():
    # Парсинг аргументов командной строки
    args = parse_cli_args()
    # Инициализация пайплайна
    pipeline = PipelineManager(args)
    #Запуск пайплайна
    pipeline.run_pipeline()

if __name__ == '__main__':
    main()