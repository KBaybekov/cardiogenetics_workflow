import yaml

def load_yaml(file_path):
    """
    Универсальная функция для загрузки данных из YAML-файла.
    
    :param file_path: Путь к YAML-файлу
    :return: Словарь с данными из YAML-файла
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)