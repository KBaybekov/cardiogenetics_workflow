from src import *
from src.utils import load_yaml

def main():
    # Парсинг аргументов командной строки
    args = parse_cli_args()

    # Загрузка конфигураций и команд в зависимости от места запуска (place)
    commands = load_yaml(file_path='config/commands.yaml')

    # Инициализация пайплайна
    pipeline = PipelineManager(args)

    # Запуск стадий пайплайна
    stage_runner = StageRunner(pipeline.__dict__, stage)
    for stage in args.stage.split(','):
        stage_runner.run_stage(stage)

if __name__ == '__main__':
    main()