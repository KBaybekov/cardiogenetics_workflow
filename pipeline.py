#! /usr/env/bin/python3

from src import cli, pipeline_manager

def main():
    # Парсинг аргументов командной строки
    args = cli.parse_cli_args()
    # Инициализация пайплайна
    pipeline = pipeline_manager.PipelineManager(args)
    #Запуск пайплайна
    pipeline.run_pipeline()

if __name__ == '__main__':
    main()