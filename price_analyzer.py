import os
import pandas as pd
import glob
from tabulate import tabulate


class PriceAnalyzer:
    def __init__(self, directory="PRICE"):
        self.directory = directory
        self.data = pd.DataFrame()

    # Метод для загрузки прайс-листов
    def load_prices(self):
        # Ищем все файлы, содержащие слово "price" в названии
        files = glob.glob(os.path.join(self.directory, '*price*.csv'))
        
        # Задаем возможные имена столбцов
        name_columns = ['название', 'продукт', 'товар', 'наименование']
        price_columns = ['цена', 'розница']
        weight_columns = ['фасовка', 'масса', 'вес']
        
        # Загружаем данные из каждого файла
        for file in files:
            df = pd.read_csv(file, delimiter=',', encoding='utf-8')
            # Определяем нужные столбцы
            name_col = next((col for col in df.columns if col.lower() in name_columns), None)
            price_col = next((col for col in df.columns if col.lower() in price_columns), None)
            weight_col = next((col for col in df.columns if col.lower() in weight_columns), None)
            
            # Если все необходимые столбцы найдены, добавляем файл к данным
            if name_col and price_col and weight_col:
                df_filtered = df[[name_col, price_col, weight_col]].copy()
                df_filtered.columns = ['Наименование', 'Цена', 'Вес']
                df_filtered['Файл'] = os.path.basename(file)
                df_filtered['Цена за кг'] = (df_filtered['Цена'] / df_filtered['Вес']).round(2)
                self.data = pd.concat([self.data, df_filtered], ignore_index=True)

    # Метод для экспорта данных в HTML файл
    def export_to_html(self, data_to_export, output_file="prices.html"):
        html_content = f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Результаты поиска цен</title>
                </head>
                <body>
                    {data_to_export.to_html(index=False)}
                </body>
            </html>
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Данные экспортированы в файл: {output_file}")

    # Метод для поиска товаров по фрагменту названия
    def find_text(self, search_text):
        # Фильтруем строки, содержащие фрагмент текста в столбце "Наименование"
        results = self.data[self.data['Наименование'].str.contains(search_text, case=False, na=False)]
        # Сортируем по цене за килограмм
        results_sorted = results.sort_values(by='Цена за кг')
        return results_sorted

    # Метод для взаимодействия с пользователем
    def start_console_interface(self):
        results = None
        while True:
            search_text = input("\nВведите название товара для поиска (или 'exit' | 'выход' для выхода): ")
            if search_text.lower() == 'exit' or search_text.lower() == 'выход':
                print("Работа завершена.")
                break
            else:
                results = self.find_text(search_text)
                if not results.empty:
                    # Выводим данные в консоль в табличной форме
                    print(tabulate(results, headers='keys', showindex=True, tablefmt='grid'))
                else:
                    print("Ничего не найдено.")
        
        # После выхода спрашиваем, нужен ли экспорт
        export_choice = input("Нужен ли экспорт данных в HTML файл? (да/нет): ").strip().lower()
        if export_choice == 'да':
            if results is None or results.empty:
                print("Нет данных для экспорта")
            else:
                output_file = input("Введите имя файла для экспорта (по умолчанию 'prices.html'): ").strip() or "prices.html"
                self.export_to_html(results, output_file)
        print("Программа завершила работу.")


# Использование класса

if __name__ == "__main__":
    analyzer = PriceAnalyzer(directory="PRICE")
    analyzer.load_prices()  # Загружаем данные из всех прайс-листов
    analyzer.start_console_interface()  # Запускаем консольный интерфейс
