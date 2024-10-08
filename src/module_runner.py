from src.utils import generate_sample_list, generate_cmd_data, save_yaml, get_paths, create_paths
from src.pipeline_manager import PipelineManager
from src.command_executor import CommandExecutor
import os

class ModuleRunner:
    def __init__(self, pipeline_manager: PipelineManager):
        #Данные, получаемые из pipeline_manager.modules_template
        self.folders: dict
        self.source_extension: str
        self.filenames: dict
        self.commands: dict
        
        # Собственные данные класса
        self.cmd_data: dict

        self.pipeline_manager = pipeline_manager


    def run_module(self, module:str, module_result_dict:dict) -> dict:
        # Алиас
        x = self.pipeline_manager

        # Загружаем данные о модуле в пространство класса
        self.load_module(x.modules_template[module], x.input_dir, x.output_dir)

        # Получаем список образцов
        self.samples = generate_sample_list(x.include_samples, x.exclude_samples, x.input_dir, self.source_extension)
        # Генеририруем команды
        self.cmd_data = generate_cmd_data(args=x.__dict__, folders=self.folders,
                                    executables=x.executables, filenames=self.filenames,
                                    cmds_dict=self.commands, commands=x.cmds_template, samples=self.samples)
        # Логгируем сгенерированные команды для модуля
        save_yaml(f'cmd_data_{module}', x.log_dir, self.cmd_data)
        # Если режим демонстрации активен, завершаем выполнение
        if x.demo == 'yes':
            return

        # Алиас
        c = self.cmd_data

        module_result_dict[module] = {'status': True, 'samples':{}}

        # Создаём пути
        create_paths(self.folders)
        print(x.log_space)
        # Инициализируем CommandExecutor
        exe = CommandExecutor(cmd_data=c, log_space=x.log_space, module=module)

        # Выполняем команды для каждого образца
        print(f'Module: {module}')
        module_result_dict = exe.execute(c.keys(), module_result_dict[module])
        
        if not module_result_dict[module]['status']:
            module_result_dict['status'] = False

        return module_result_dict
        

    def load_module(self, data:dict, input_dir:str, output_dir:str):
        """
        Загружает данные о модуле, обрабатывает их с использованием переменных в пространстве класса и\
                добавляет их в пространство объекта класса.
        """
        # Составляем полные пути для папок
        data['folders'] = get_paths(data['folders'], input_dir, output_dir)
        # Устанавливаем атрибут modules_data в пространство экземпляра класса
        for key,value in data.items():
            setattr(self, key, value)


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
                    for module in stages}
        source_extensions = {module: {all_stages_vars[module]['source_extension']}
                            for module in stages}
        # Возвращаем словарь с путями
        return folders, source_extensions