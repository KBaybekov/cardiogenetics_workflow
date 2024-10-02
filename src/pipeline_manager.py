from utils import *
from stage_runner import StageRunner
import os
from datetime import date

class PipelineManager:
    def __init__(self, args):
        """
        Конструктор, принимающий аргументы командной строки и инициализирующий параметры пайплайна.
        """
        # Преобразование args в словарь
        self.args = vars(args)

        # Инициализируем окружения и бинарные файлы
        self.current_dir = os.getcwd()
        self.envs, self.binaries = self.get_env_list(self.args['place'])
        self.all_stages_vars = load_yaml('config/stage_vars.yaml')
        self.folders, self.extensions = self.get_stage_vars(self.args['stage'], self.input_dir, self.output_dir, self.all_stages_vars)
        self.today = date.today().strftime('%d.%m.%Y')

        # Логи
        self.log_dir = os.path.join(self.args['output_dir'], 'Logs/', f'{self.today}_{'-'.join(self.args['stage'])}')
        self.log = f'{self.log_dir}/stdout_log.txt'
        self.errlog = f'{self.log_dir}/stderr_log.txt'
        self.log_dict = os.path.join(self.log_dir, 'log.yaml')
        self.errlog_dict = os.path.join(self.log_dir, 'err_log.yaml')

        # Преобразуем все начальные параметры в словарь
        self.init_configs = vars(self)
        # Извлекаем в отдельный словарь пути к файлам логов
        self.logs = {k: v for k, v in self.init_configs.items() if k in ['log', 'errlog', 'log_dict', 'errlog_dict']}
        # Сохраняем все начальные параметры в лог
        save_yaml('init_configs', self.log_dir, self.init_configs)
        

        # Запускаем пайплайн
        self.run_pipeline(stages=self.args['stage'], args=self.args, envs=self.envs,
                          binaries=self.binaries, folders=self.folders,
                          extensions=self.extensions, logs=self.logs)

    def get_stage_vars(self, stages: list, input_dir:str, output_dir:str, all_stages_vars:dict):
        """
        Создаёт директории на основе stage_vars, не обращаясь напрямую к input_dir и output_dir.
        
        :param stages: Список этапов пайплайна
        :param input_dir: Путь к директории для входных данных
        :param output_dir: Путь к директории для выходных данных
        :param all_stages_vars: Словарь с информацией о папках и расширениях для каждого этапа пайплайна
        :return: Словарь с полными путями к созданным директориям
        """

        # Создаём список директорий для каждого этапа
        folders  = {
            stage: {
                **{key: os.path.join(input_dir, f'{value}/') for key, value in all_stages_vars[stage]['folders'].get('input_dir', {}).items()},
                **{key: os.path.join(output_dir, f'{value}/') for key, value in all_stages_vars[stage]['folders'].get('output_dir', {}).items()}
            }
            for stage in stages
        }

        extensions = {stage: {all_stages_vars[stage]['extension']}
            for stage in stages}

        # Возвращаем словарь с путями
        return folders, extensions

    def get_env_list(self, place):
        """
        Загружает окружения и бинарные файлы из YAML-файла для заданного места (place).
        
        :param place: Место выполнения пайплайна
        :return: Словарь окружений и бинарных файлов
        """
        # Загружаем окружения и бинарные файлы из envs.yaml
        env_config = load_yaml('config/envs.yaml')[place]
        envs = env_config['envs']
        binaries = env_config['binaries']
        return envs, binaries

    def run_pipeline(self, stages:list, args:dict, envs:dict, binaries:dict, folders:dict, extensions:dict, logs:dict):
        """
        Основной метод для запуска всех стадий пайплайна.
        
        :param stages: Список этапов пайплайна
        :param args: Аргументы командной строки
        :param envs: Словарь с окружениями
        :param binaries: Словарь с путями к бинарным файлам
        :param folders: Словарь с директориями для каждой стадии
        :param extensions: Словарь с расширениями для файлов каждой стадии
        :param logs: Словарь с путями к логам
        """
        for stage in stages:
            print(f'Running stage: {stage}')
            # Создаём директории для результатов
            for path in folders[stage].values():
                os.makedirs(path, exist_ok=True)
            # Формирование пула команд и их выполнение
            StageRunner(self).run_stage(stage)