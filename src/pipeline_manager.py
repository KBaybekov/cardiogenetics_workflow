from utils import *
from module_runner import ModuleRunner
import os
from datetime import date

class PipelineManager:
    def __init__(self, args):
        """
        Конструктор, принимающий аргументы командной строки и инициализирующий параметры пайплайна.
        """
        # Преобразование args в словарь
        self.args = vars(args)

        # Получаем данные о запуске
        self.current_dir = os.getcwd()
        self.today = date.today().strftime('%d.%m.%Y')

        # Загружаем переменные для каждой стадии пайплайна
        self.folders, self.source_extensions = self.get_stage_vars(self.args['module'], self.input_dir, self.output_dir, self.all_stages_vars)
        

        # Логи
        self.log_dir = os.path.join(self.args['output_dir'], 'Logs/', f'{self.today}_{'-'.join(self.args['module'])}')
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

    def load_machine_vars(self, config_path:str, machine:str):
        """
        Загружает данные о средах и исполняемых файлах указанной машины, необходимых для пайплайна, и добавляет их в пространство объекта класса.
        
        :param path: Путь к директории, где хранится YAML-файл.
        :param machine: Наименование машины, использованное в YAML-файле.
        """
        # Загружаем данные из YAML-файла
        machine_data = load_yaml(file_path=f'{config_path}machines.yaml', subsection=machine)
        envs = machine_data.get('envs', {})
        binaries = machine_data.get('binaries', {})
        env_command_template = machine_data.get('env_command', '')

        # Создаём атрибут executables
        executables = {}
        # Проходим по всем ключам в binaries
        for key, binary in binaries.items():
            if key in envs:
                # Если ключ есть в envs, заменяем команду по шаблону env_command
                executables.update({key: env_command_template.replace('env', envs[key]).replace('binary', binary)})
            else:
                # Если ключа нет в envs, оставляем значение из binaries
                executables.update({key: binary})
        # Устанавливаем атрибут executables в пространство экземпляра класса
        setattr(self, 'executables', executables)

    def run_pipeline():


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
            module: {
                **{key: os.path.join(input_dir, f'{value}/') for key, value in all_stages_vars[module]['folders'].get('input_dir', {}).items()},
                **{key: os.path.join(output_dir, f'{value}/') for key, value in all_stages_vars[module]['folders'].get('output_dir', {}).items()}
            }
            for module in stages
        }

        source_extensions = {module: {all_stages_vars[module]['source_extension']}
            for module in stages}

        # Возвращаем словарь с путями
        return folders, source_extensions