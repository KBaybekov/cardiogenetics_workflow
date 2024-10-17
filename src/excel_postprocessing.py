#!/usr/bin/env python3

import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
import sys
import warnings

warnings.simplefilter("ignore")

def read_tsv(file):
    """
    Чтение TSV файла. Возвращает два DataFrame: один для данных, второй для шапки (метаинформации).
    """
    with open(file, 'r') as f:
        header_lines = []
        data_lines = []

        for line in f:
            if line.startswith('#'):
                header_lines.append(line.strip())
            else:
                data_lines.append(line.strip())
        
        # Преобразование шапки в DataFrame
        header_data = []
        for line in header_lines:
            # Убираем "Column description. " и "#", затем разделяем по "="
            line = line.replace("#", "").replace("Column description. ", "")
            if "=" in line:
                key, value = line.split("=", 1)
                header_data.append([key.strip(), value.strip()])
        
        header_df = pd.DataFrame(header_data, columns=["Тип данных", "Значение"])
        
        # Преобразование данных в DataFrame
        from io import StringIO
        data_str = '\n'.join(data_lines)
        data_df = pd.read_csv(StringIO(data_str), sep='\t')
        if 'uid' in data_df.columns:
            data_df = data_df.drop(columns=['uid'])

    return data_df, header_df


def create_excels(data_df:pd.DataFrame, header_df:pd.DataFrame, output_file:str, var_threshold:float):
    """
    Создает 2 Excel-файла (один со всеми частотами, другой (клинический) - с частотами не более указанной).\n
    Файлы с двумя листами: один для данных, другой для шапки.
    """

    dfs = reform_data(data_df, var_threshold, output_file)

    for filepath, df in dfs.items():
        wb = add_header_sheet(design_data_df(df), header_df)
        # Сохранение файла
        wb.save(filepath)


def reform_data(data_df:pd.DataFrame, var_threshold:float, output_file:str) -> dict:
    add_varsome_column(data_df)
    # Перемещение большинства колонок 'Extra VCF Info, Original_input' в конец;  важных из Extra VCF Info - в начало
    important_cols = ['SRF', 'SRR', 'SAF', 'SAR']
    alt_base_idx = data_df.columns.get_loc('alt_base') + 1
    df_cols = data_df.columns.values
    for col in df_cols:
        if 'extra_vcf_info' in col:
            if any(important_col in col for important_col in important_cols):
                data_df.insert(alt_base_idx + 1, col, data_df.pop(col))
            else:
                extra_vcf_info_col = data_df.pop(col)
                data_df[col] = extra_vcf_info_col
        if 'Original_input' in col:
            original_input_col = data_df.pop(col)
            data_df[col] = original_input_col
    # перемещение налево Gnomad Global AF
    for col in ['gnomad.af', 'gnomad4.af']:
        if col in data_df.columns.values:
            data_df.insert(alt_base_idx + 1, col, data_df.pop(col))
    # AF ставим всё же левее всех остальных
    data_df.insert(alt_base_idx + 1, 'extra_vcf_info.AF', data_df.pop('extra_vcf_info.AF'))
    clinical_data_df = data_df[data_df['gnomad.af'] <= var_threshold]
    return {output_file:data_df, output_file.replace('.xlsx', '_clinical.xlsx'):clinical_data_df}

def add_varsome_column(data_df):
    """
    Добавляет новый столбец 'Varsome' в DataFrame, который содержит ссылки на varsome 
    для каждого варианта, основанные на значениях в столбцах координат.
    """
    # Создаём новый столбец для VarSome
    data_df['Varsome'] = ''

    # Итерация по строкам DataFrame
    for index, row in data_df.iterrows():
        var_ids = []
        # Объединяем значения из столбцов координат, пропуская "-"
        for col in range(4):
            if row[col] != "-":
                var_ids.append(str(row[col]))
            else:
                if col == 2:
                    var_ids.append('-')
        
        # Создаём строку из идентификаторов, разделённых дефисами
        if var_ids:
            var_string = "-".join(var_ids).replace('---', '--')
            # Формируем ссылку на varsome
            data_df.at[index, 'Varsome'] = f"https://varsome.com/variant/hg38/{var_string}?annotation-mode=germline"


def design_data_df(df:pd.DataFrame) -> Workbook:
    wb = Workbook()
    
    # Лист для данных
    ws_data = wb.active
    ws_data.title = "Данные"

    for r in dataframe_to_rows(df, index=False, header=True):
        ws_data.append(r)

    # Применение цветовой кодировки к Gnomad Global AF
    for col in ['gnomad.af', 'gnomad4.af']:
        if col in df.columns.values:
            global_af_colors = df[col].apply(colorize_global_af)
            # Добавляем форматы в Excel после создания листа
            for idx, color in enumerate(global_af_colors, start=2):  # Индексация с 2, чтобы пропустить заголовок
                cell = ws_data.cell(row=idx, column=df.columns.get_loc(col) + 1)
                cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    
    format_dataframe(ws_data, df)
    # Добавление проверки данных (пример для первой колонки)
    #add_data_validation(ws_data, df, 'A')
    return wb

def colorize_global_af(val:float) -> str:
    """Возвращает цвет в зависимости от значения 'Global AF'."""
    if pd.isnull(val) or val < 0.01:
        return "FF0000"  # Красный
    elif 0.01 <= val <= 0.05:
        return "FFFF00"  # Жёлтый
    elif val > 0.05:
        return "00FF00"  # Зелёный
    return "FFFFFF"  # Белый для пустых значений

def format_dataframe(ws, df, max_width=15):
    """
    Форматирует DataFrame в Excel: добавляет жирный шрифт к заголовкам, 
    устанавливает оптимальную ширину колонок, добавляет автофильтр и
    прибавляет 3 символа к ширине колонок для учёта кнопки автофильтра.
    """
    for idx, col in enumerate(df.columns):
        # Жирный шрифт для заголовков, выравнивание по центру
        cell = ws.cell(row=1, column=idx+1)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

        # Определяем оптимальную ширину для каждой колонки
        series = df[col].astype(str)
        max_len = max(series.map(len).max(), len(col)) + 6
        # Если длина текста больше максимальной ширины, устанавливаем максимальную ширину
        column_width = min(max_len + 2, max_width)  # Добавляем 2 символа для лучшей читабельности
        ws.column_dimensions[get_column_letter(idx+1)].width = column_width

    # Добавляем автофильтр для всех колонок
    ws.auto_filter.ref = ws.dimensions

def add_header_sheet(wb:Workbook, header_df:pd.DataFrame) -> Workbook:
    # Лист для шапки
    ws_header = wb.create_sheet(title="Описание")
    
    for r in dataframe_to_rows(header_df, index=False, header=True):
        ws_header.append(r)
    
    format_dataframe(ws_header, header_df)

    return wb


def add_data_validation(ws, df, column_letter):
    """
    Добавляет проверку данных в столбец.
    """
    df_len = len(df)
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    dv.ranges.add(f'{column_letter}2:{column_letter}{df_len+1}')
    ws.add_data_validation(dv)


def main():
    """
    Основная функция. Читает входной TSV файл, преобразует его и сохраняет в Excel.
    """
    if len(sys.argv) != 4:
        print("Использование: script.py in.tsv out.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    var_threshold = float(sys.argv[3])

    # Чтение TSV файла
    data_df, header_df = read_tsv(input_file)

    # Создание Excel-файлов
    create_excels(data_df, header_df, output_file, var_threshold)


if __name__ == "__main__":
    main()