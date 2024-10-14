#!/usr/bin/env python3

import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
import sys

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

def format_dataframe(ws, df, max_width=30):
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

def add_data_validation(ws, df, column_letter):
    """
    Добавляет проверку данных в столбец.
    """
    df_len = len(df)
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    dv.ranges.add(f'{column_letter}2:{column_letter}{df_len+1}')
    ws.add_data_validation(dv)

def create_excel(file, data_df, header_df, output_file):
    """
    Создает Excel файл с двумя листами: один для данных, другой для шапки.
    """
    wb = Workbook()
    
    # Лист для данных
    ws_data = wb.active
    ws_data.title = "Данные"
    
    for r in dataframe_to_rows(data_df, index=False, header=True):
        ws_data.append(r)
    
    format_dataframe(ws_data, data_df)

    # Добавление проверки данных (пример для первой колонки)
    add_data_validation(ws_data, data_df, 'A')
    
    # Лист для шапки
    ws_header = wb.create_sheet(title="Описание")
    
    for r in dataframe_to_rows(header_df, index=False, header=True):
        ws_header.append(r)
    
    format_dataframe(ws_header, header_df)
    
    # Сохранение файла
    wb.save(output_file)

def main():
    """
    Основная функция. Читает входной TSV файл, преобразует его и сохраняет в Excel.
    """
    if len(sys.argv) != 3:
        print("Использование: script.py in.tsv out.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Чтение TSV файла
    data_df, header_df = read_tsv(input_file)

    # Создание Excel файла
    create_excel(input_file, data_df, header_df, output_file)

if __name__ == "__main__":
    main()
