from src.utils import load_templates, save_yaml
import os
from datetime import date

class PipelineManager:
    """
    Основной класс для управления пайплайном. Инициализирует конфигурации и логи, загружает данные о машине и модулях.
    """
    machines_template: dict
    modules_template: dict
    cmds_template: dict

    def __init__(self, args:dict):
        """
        Конструктор, принимающий аргументы командной строки и инициализирующий параметры пайплайна.
        """
        # Объявляем основные атрибуты
        self.config_path:str
        self.log_dir:str
        self.modules:list
        self.input_dir:str
        self.output_dir:str
        self.machine:str
        self.include_samples:list
        self.exclude_samples:list
        self.executables: dict
        self.demo:str
        
        # Добавляем все элементы args как атрибуты класса
        for key, value in args.items():
            setattr(self, key, value)

        # Получаем данные о запуске
        self.current_dir = os.getcwd()
        self.today = date.today().strftime('%d.%m.%Y')

        # Логи
        self.set_logs()

        # Загружаем данные конфигов
        load_templates(self.config_path)
        
        # Загрузка конфигурации машины
        self.load_machine_vars()
        
        # Преобразуем все начальные параметры в словарь
        self.init_configs = vars(self)
        # Сохраняем все начальные параметры в лог
        save_yaml('init_configs', self.log_dir, self.init_configs)


    def set_logs(self):
        """
        Инициализирует директории для логов и сохраняет пути к файлам логов в атрибуты класса.
        """
        # Устанавливаем директорию для логов
        self.log_dir = os.path.join(self.output_dir, 'Logs/', f'{self.today}_{"-".join(self.modules)}')
        
        # Устанавливаем пути к файлам логов
        self.stdout_log = f'{self.log_dir}/stdout_log.txt'
        self.stderr_log = f'{self.log_dir}/stderr_log.txt'
        self.log_data = os.path.join(self.log_dir, 'log.yaml')
        self.status_log = os.path.join(self.log_dir, 'status_log.yaml')
        
        # Создаём словарь с путями к файлам логов
        self.log_space = {
            'log_dir': self.log_dir,
            'stdout_log': self.stdout_log,
            'stderr_log': self.stderr_log,
            'log_data': self.log_data,
            'status_log': self.status_log
        }


    def load_machine_vars(self):
        """
        Загружает данные о средах и исполняемых файлах указанной машины, необходимых для пайплайна, формирует команды для вызова программ \
            и добавляет их в пространство объекта класса.
        """
        machine_data:dict
        binaries:dict
        # Загружаем данные из шаблона
        machine_data = self.machines_template[self.machine]
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
        self.executables = executables


    def run_pipeline(self):
        """
        Запуск всего пайплайна по модулям.
        """
        from src.module_runner import ModuleRunner
        # Инициализируем ModuleRunner с текущим экземпляром PipelineManager
        module_runner = ModuleRunner(self)

        result_dict = {'status':True, 'modules':{}}

        # Проходим по каждому модулю, указанному в аргументах
        for module in self.modules:
            print(f'Запуск модуля: {module}')

            # Запускаем модуль через ModuleRunner
            result_dict = module_runner.run_module(module, result_dict['modules'])
            
            # Если хотя бы один модуль завершился с ошибкой, обновляем статус пайплайна
            if not result_dict['modules'][module]['status']:
                result_dict['status'] = False

        if result_dict['status']:
            print("Пайплайн завершён успешно.")
        else:
            print("Пайплайн завершён с ошибками:")
            for module, module_data in result_dict['modules']:
                if not module_data['status']:
                    print(f'Модуль: {module}')
                    for sample, sample_data in result_dict['modules'][module][module_data].items():
                        if not sample_data['status']:
                            print(f'\t{sample}')
                            for programm, exit_code in sample_data.items():
                                print(f'\t\t{programm}: exit code {exit_code}')

        save_yaml(filename=self.status_log, data=result_dict)