import yaml
import os

def load_yaml(file_path:str, subsection:str = ''):
    """
    Универсальная функция для загрузки данных из YAML-файла.

    :param file_path: Путь к YAML-файлу. Ожидается строка, указывающая на местоположение файла с данными.
    :param subsection: Опциональный параметр. Если передан, функция вернёт только данные из указанной
                       секции (например, конкретного этапа пайплайна). Если пусто, возвращаются все данные.
                       По умолчанию - пустая строка, что означает возврат всего содержимого файла.
    
    :return: Возвращает словарь с данными из YAML-файла. Если указан параметр subsection и он присутствует
             в YAML, возвращается соответствующая секция, иначе — всё содержимое файла.
    """
    # Открываем YAML-файл для чтения
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)  # Загружаем содержимое файла в словарь с помощью safe_load
    
    # Если subsection не указан, возвращаем весь YAML-файл
    if subsection == '':
        return data
    else:
        # Если subsection указан и существует в файле, возвращаем только эту секцию
        if subsection  in data.keys():
            return data[subsection]
        else:
            raise ValueError(f"Раздел '{machine}' не найден в {file_path}")
        
def save_yaml(filename, path, data):
    """
    Сохраняет словарь в файл в формате YAML.
    
    :param filename: Имя файла для сохранения (например, 'config.yaml')
    :param path: Путь к директории, где будет сохранён файл
    :param data: Словарь с данными, которые нужно сохранить в YAML
    """
    # Полный путь к файлу
    file_path = f'{path}{filename}.yaml'

    # Записываем данные в YAML-файл
    with open(file_path, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)

def load_templates(path: str = 'local_configs/'):
    """
    Загружает конфигурационные файлы (machines, modules, samples) из указанной директории.
    Выдаёт ошибку в случае отсутствия файла или проблем с его загрузкой.

    :param path: Путь к директории, где хранятся конфигурационные YAML-файлы.
    """
    required_files = ['machines_template', 'modules_template', 'cmds_template']
    loaded_configs = {}

    # Проходим по списку обязательных файлов
    for req_file in required_files:
        file_path = os.path.join(path, f'{req_file}.yaml')
        
        # Проверяем наличие файла
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Файл {req_file}.yaml не найден в директории {path}")
        
        # Пытаемся загрузить файл
        try:
            with open(file_path, 'r') as f:
                loaded_configs[req_file] = yaml.safe_load(f)  # Загружаем содержимое файла
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка загрузки файла {req_file}.yaml: {e}")
    
    # Сохраняем загруженные конфигурации как глобальные переменные
    for var_name, config_data in loaded_configs.items():
        globals()[var_name] = config_data

        

def get_paths(folders: dict, input_dir: str, output_dir: str) -> dict:
    """
    Создаёт словарь с путями для всех директорий, указанных в словаре 'folders',
    где для каждой директории указан путь относительно 'input_dir' или 'output_dir'.

    :param folders: Словарь с поддиректориями для 'input_dir' и 'output_dir'
    :param input_dir: Базовая директория для 'input_dir'
    :param output_dir: Базовая директория для 'output_dir'
    :return: Словарь с абсолютными путями к каждой директории
    """
    # Формируем словарь директорий с полными путями
    folders_with_paths = {
        # Проходим по всем директориям в 'input_dir' и добавляем базовый путь 'input_dir'
        **{key: os.path.join(input_dir, f'{value}/') for key, value in folders.get('input_dir', {}).items()},
        # Проходим по всем директориям в 'output_dir' и добавляем базовый путь 'output_dir'
        **{key: os.path.join(output_dir, f'{value}/') for key, value in folders.get('output_dir', {}).items()}
    }
    return folders_with_paths


def generate_cmd_data(args:dict, folders:dict,
                        executables:dict,
                        filenames:dict, commands:dict,
                        samples:list):

    cmd_data = {}
    for sample in samples:
        sample_filenames = generate_sample_filenames(sample, folders, filenames)
        commands = generate_commands(args, folders, executables, sample_filenames, commands)
        cmd_data[sample] = commands
    return cmd_data


def generate_sample_list(in_samples: list, ex_samples: list,
                         input_dir: str, extension: str):
    """
    Генерирует список файлов на основе включающих и исключающих образцов.
    Выдаёт ошибку, если итоговый список пустой.

    :param in_samples: Список образцов, которые нужно включить.
    :param ex_samples: Список образцов, которые нужно исключить.
    :param input_dir: Директория, где искать файлы.
    :param extension: Расширение файлов для поиска.
    :return: Список путей к файлам.
    """
    # Ищем все файлы в директории с указанным расширением
    samples = [s for s in os.listdir(input_dir) if s.endswith(extension)]
    # Если список включающих образцов непустой, фильтруем по нему
    if len(in_samples) != 0:
        samples = [s for s in samples if any(inclusion in s for inclusion in in_samples)]
    # Если список исключающих образцов непустой, фильтруем по нему
    if len(ex_samples) != 0:
        samples = [s for s in samples if not any(exclusion in s for exclusion in ex_samples)]
    # Если итоговый список пустой, выдаём ошибку
    if not samples:
        raise ValueError("Итоговый список образцов пуст. Проверьте входные и исключаемые образцы, а также директорию с исходными файлами.")
    # Возвращаем полный путь к каждому файлу
    return [os.path.join(input_dir, s) for s in samples]


def generate_sample_filenames(sample: str, folders: dict, filenames: dict) -> dict:
    """
    Генерирует словарь с путями к файлам для сэмпла на основе инструкций в filenames.

    :param sample: Имя сэмпла (строка).
    :param folders: Словарь с путями к директориям.
    :param filenames: Словарь с инструкциями для генерации файловых путей.
    :return: Словарь с результатами выполнения инструкций для файловых путей.
    """
    # Словарь для хранения сгенерированных путей
    generated_filenames = {}

    # Проходим по каждому ключу в filenames и вычисляем значение
    for key, instruction in filenames.items():
        # Используем eval() для вычисления выражений в строках
        try:
            # Выполняем инструкцию, подставляя доступные переменные
            generated_filenames[key] = eval(instruction, {'sample': sample, 'folders': folders, 'filenames': generated_filenames,})
        except Exception as e:
            print(f"Ошибка при обработке {key}: {e}")
    
    return generated_filenames


def generate_commands(executables:dict, folders:dict, args:dict, filenames:dict,
                      commands:dict):
    """
    Генерирует словарь с командами для сэмпла на основе инструкций в cmds_template.

    :param executables: Словарь со строками для вызова программ.
    :param folders: Словарь с путями к директориям.
    :param filenames: Словарь с именами для файлов.
    :param args: Словарь с аргументами для команд.
    :param commands: Словарь с инструкциями для создания команд.
    :return: Словарь с результатами выполнения инструкций для команд.
    """
    # Словарь для хранения сгенерированных путей
    generated_cmds = {}

    # Проходим по каждому ключу в filenames и вычисляем значение
    for key, instruction in commands.items():
        # Используем eval() для вычисления выражений в строках
        try:
            # Выполняем инструкцию, подставляя доступные переменные
            generated_cmds[key] = eval(instruction, {'programms': executables, 'folders': folders, 'filenames': filenames,'args': args})
        except Exception as e:
            print(f"Ошибка при обработке {key}: {e}")
    return generated_cmds