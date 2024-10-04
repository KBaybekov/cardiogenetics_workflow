from utils import *
from module_runner import ModuleRunner
import os
from datetime import date

class PipelineManager:
    #Объявляем переменные конфигов
    machines_template: dict
    modules_template: dict
    cmds_template: dict

    def __init__(self, args):
        """
        Конструктор, принимающий аргументы командной строки и инициализирующий параметры пайплайна.
        """
        #Объявляем переменные класса
        self.config_path:str
        self.log_dir:str
        self.modules:list
        self.input_dir:str
        self.output_dir:str
        self.machine:str
        self.include_samples:list
        self.exclude_samples:list
        self.executables: dict

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
        
        # Загрузка конфигурации машины и конфигурации модулей из шаблонов; шаблон cmds_template будет преобразован в ModuleRunner
        self.load_machine_vars()
        
        # Преобразуем все начальные параметры в словарь
        self.init_configs = vars(self)
        # Сохраняем все начальные параметры в лог
        save_yaml('init_configs', self.log_dir, self.init_configs)


    def set_logs(self):
        setattr(self, 'log_dir', os.path.join(self.output_dir, 'Logs/', f'{self.today}_{'-'.join(self.modules)}'))
        setattr(self, 'log', f'{self.log_dir}/stdout_log.txt')
        setattr(self, 'errlog', f'{self.log_dir}/stderr_log.txt')
        setattr(self, 'log_dict', os.path.join(self.log_dir, 'log.yaml'))
        setattr(self, 'errlog_dict', os.path.join(self.log_dir, 'err_log.yaml'))
        # Извлекаем в отдельный словарь пути к файлам логов
        self.logs = {k: v for k, v in self.init_configs.items() if k in ['log_dir', 'log', 'errlog', 'log_dict', 'errlog_dict']}

    def load_machine_vars(self):
        """
        Загружает данные о средах и исполняемых файлах указанной машины, необходимых для пайплайна, формирует команды для вызова программ \
            и добавляет их в пространство объекта класса.
        """
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
        setattr(self, 'executables', executables)


    def run_pipeline(self):
        """
        Запуск всего пайплайна по модулям.
        """
        # Инициализируем ModuleRunner с текущим экземпляром PipelineManager
        module_runner = ModuleRunner(self)

        # Проходим по каждому модулю, указанному в аргументах
        for module in self.modules:
            print(f'Запуск модуля: {module}')

            # Запускаем модуль через ModuleRunner
            result = module_runner.run_module(module)
            
            if result != 0:
                print(f'Модуль {module} завершился с ошибкой.')
                break  # Останавливаем процесс, если какой-то модуль завершился с ошибкой

        print("Пайплайн завершён успешно.")