import yaml

def load_yaml(file_path):
    """
    Универсальная функция для загрузки данных из YAML-файла.
    
    :param file_path: Путь к YAML-файлу
    :return: Словарь с данными из YAML-файла
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
    
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