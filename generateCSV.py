import csv
import json
import headerCSV
import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser

def load_settings(file_path="default_settings.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        settings = json.load(file)
    return settings

def show_about_window():
    about_dialog = tk.Toplevel()
    about_dialog.title("О программе")

    info_texts = [
        "Основная цель программы - преобразование исходного CSV файла\n"
        "в UML use case diagram который импортируется в drawio\n"
        "для построения схемы-зависимостей",
        "Контакты: kryukovn18@gmail.com",
        "Ниже можно скачать пример файла\n"
        "В примере указана структура файла,\n"
        "которая корректно преобразуется.\n\n"
        "Важно, чтобы были указаны все существующие заголовки\n"
        "отсутствие в них данных не влияет на результат\n\n"
        "Зависимости происходят от указанных сервисов"
    ]

    for row, text in enumerate(info_texts):
        tk.Label(about_dialog, text=text, font=("Arial", 10)).grid(row=row, column=0, padx=20, pady=5)

    def download_example_file():
        resource_path = os.path.join(os.path.dirname(__file__), "resources", "exampleCSV.csv")
        if os.path.exists(resource_path):
            save_path = filedialog.asksaveasfilename(
                title="Сохранить пример CSV",
                initialfile="exampleCSV.csv",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if save_path:
                with open(resource_path, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                messagebox.showinfo("Успех", "Файл успешно скачан")
        else:
            messagebox.showerror("Ошибка", "Файл exampleCSV.csv не найден в ресурсах программы")
    tk.Button(about_dialog, text="Скачать пример исходного CSV файла", command=download_example_file).grid(row=3, column=0, padx=20, pady=10)

    def on_next():
        about_dialog.destroy()
    tk.Button(about_dialog, text="Далее", command=on_next).grid(row=4, column=0, pady=10)
    about_dialog.wait_window()

def get_column_order(settings):
    dialog = tk.Toplevel()
    dialog.title("Настройки")
    column_options = settings["default_column_order"]

    input_file_var = tk.StringVar(value="")
    output_file_var = tk.StringVar(value="generatedCSV.csv")

    combos = []
    for i, option in enumerate(column_options):
        tk.Label(dialog, text=f"Колонка {i + 1}:").grid(row=i, column=0, padx=10, pady=5, sticky="w")
        combo = tk.StringVar(value=option)
        dropdown = tk.OptionMenu(dialog, combo, *column_options)
        dropdown.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        combos.append(combo)

    use_default_size_var = tk.BooleanVar(value=True)
    use_default_color_var = tk.BooleanVar(value=True)

    tk.Checkbutton(dialog, text="Использовать размеры элементов по умолчанию?", variable=use_default_size_var).grid(row=len(column_options), column=0, columnspan=2, pady=5, sticky="w")
    tk.Checkbutton(dialog, text="Использовать цвета элементов по умолчанию?", variable=use_default_color_var).grid(row=len(column_options) + 1, column=0, columnspan=2, pady=5, sticky="w")

    def choose_input_file():
        file_path = filedialog.askopenfilename(
            title="Выберите исходный CSV-файл",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            input_file_var.set(file_path)

    def choose_output_file():
        file_path = filedialog.asksaveasfilename(
            title="Выберите место сохранения сгенерированного CSV-файла",
            initialfile="generatedCSV.csv",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            output_file_var.set(file_path)

    tk.Label(dialog, text="Исходный файл:").grid(row=len(column_options) + 2, column=0, padx=10, pady=5, sticky="w")
    tk.Entry(dialog, textvariable=input_file_var, width=30).grid(row=len(column_options) + 2, column=1, padx=10, pady=5)
    tk.Button(dialog, text="Обзор...", command=choose_input_file).grid(row=len(column_options) + 2, column=2, padx=10, pady=5)

    tk.Label(dialog, text="Выходной файл:").grid(row=len(column_options) + 3, column=0, padx=10, pady=5, sticky="w")
    tk.Entry(dialog, textvariable=output_file_var, width=30).grid(row=len(column_options) + 3, column=1, padx=10, pady=5)
    tk.Button(dialog, text="Обзор...", command=choose_output_file).grid(row=len(column_options) + 3, column=2, padx=10, pady=5)

    def set_column_order():
        choices = [column_combo.get() for column_combo in combos]
        if len(choices) != len(set(choices)):
            messagebox.showerror("Ошибка", "Каждая колонка должна быть указана только один раз")
            return

        input_file = input_file_var.get().strip()
        output_file = output_file_var.get().strip()

        if not input_file:
            messagebox.showerror("Ошибка", "Не выбран исходный файл")
            return

        dialog.input_file = input_file
        dialog.output_file = output_file
        dialog.use_default_size = use_default_size_var.get()
        dialog.use_default_color = use_default_color_var.get()
        dialog.column_order = choices
        dialog.destroy()

    ok_button = tk.Button(dialog, text="Далее", command=set_column_order)
    ok_button.grid(row=len(column_options) + 4, column=0, columnspan=3, pady=10)

    dialog.wait_window()

    if not hasattr(dialog, "input_file") or not dialog.input_file.strip():
        return None, None, None, None, None

    return (
        dialog.input_file,
        dialog.output_file,
        dialog.column_order,
        dialog.use_default_size,
        dialog.use_default_color
    )

def get_size_parameters(settings):
    dialog = tk.Toplevel()
    dialog.title("Параметры размеров элементов")
    default_size_params = settings["default_size_parameters"]

    parameters = [
        {"name": "width", "label": "Размер элемента по ширине:", "default": default_size_params["width"]},
        {"name": "height", "label": "Размер элемента по высоте:", "default": default_size_params["height"]},
        {"name": "padding", "label": "Отступ от элементов:", "default": default_size_params["padding"]},
        {"name": "nodespacing", "label": "Расстояние между узлами:", "default": default_size_params["nodespacing"]},
        {"name": "levelspacing", "label": "Расстояние между уровнями узлов:", "default": default_size_params["levelspacing"]},
        {"name": "edgespacing", "label": "Расстояние между связями:", "default": default_size_params["edgespacing"]}
    ]

    vars_dict = {}
    for idx, param in enumerate(parameters):
        label_text = param["label"]
        default_value = param["default"]

        var = tk.StringVar(value=str(default_value))
        vars_dict[param["name"]] = var

        tk.Label(dialog, text=label_text).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(dialog, textvariable=var).grid(row=idx, column=1, padx=10, pady=5, sticky="w")

    def reset_to_defaults():
        for reset_param in parameters:
            vars_dict[reset_param["name"]].set(str(reset_param["default"]))

    reset_button = tk.Button(dialog, text="Сбросить к значениям по умолчанию", command=reset_to_defaults)
    reset_button.grid(row=len(parameters), column=0, columnspan=2, pady=10)

    def on_ok():
        try:
            result = {}
            for size_param in parameters:
                value = vars_dict[size_param["name"]].get().strip()
                if size_param["name"] in ["width", "height"]:
                    result[size_param["name"]] = int(value) if value != "auto" else value
                else:
                    result[size_param["name"]] = int(value)

            dialog.result = (
                result["nodespacing"],
                result["levelspacing"],
                result["edgespacing"],
                result["width"],
                result["height"],
                result["padding"]
            )
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Должны быть указаны корректные значения")

    ok_button = tk.Button(dialog, text="Далее", command=on_ok)
    ok_button.grid(row=len(parameters) + 1, column=0, columnspan=2, pady=10)

    dialog.wait_window()
    return getattr(dialog, "result", None)

def get_color_parameters(settings):
    dialog = tk.Toplevel()
    dialog.title("Введите параметры цвета и формы")

    default_color_params = settings["default_color_parameters"]
    shape_options = settings["shape_options"]
    default_connection_colors = settings["default_connection_colors"]
    dashed_options = settings["dashed_options"]

    parameters = {
        "Топик": default_color_params["topic"],
        "База данных": default_color_params["db"],
        "Папка": default_color_params["folder"],
        "Сервис": default_color_params["service"],
        "API": default_color_params["api"]
    }

    vars_dict = {}
    canvases_dict = {}
    row_index = 0

    for category, props in parameters.items():
        frame = tk.LabelFrame(dialog, text=f"{category.capitalize()}")
        frame.grid(row=row_index // 2, column=row_index % 2, padx=10, pady=10, sticky="w")

        inner_row = 0
        for prop_name, default_value in props.items():
            var = tk.StringVar(value=default_value)
            vars_dict[f"{category}_{prop_name}"] = var

            if prop_name.endswith("color"):
                tk.Label(frame, text=f"{'Заливка' if prop_name == 'fill_color' else 'Контур'}:").grid(
                    row=inner_row, column=0, padx=5, pady=5, sticky="w"
                )
                entry = tk.Entry(frame, textvariable=var)
                entry.grid(row=inner_row, column=1, padx=5, pady=5)

                color_canvas = tk.Canvas(frame, width=20, height=20, bg=default_value, highlightthickness=1,
                                         highlightbackground="black")
                color_canvas.grid(row=inner_row, column=2, padx=5, pady=5)
                canvases_dict[f"{category}_{prop_name}"] = color_canvas

                def choose_color(color_var, canvas, background_var):
                    color = colorchooser.askcolor(initialcolor=color_var.get())[1]
                    if color:
                        color_var.set(color)
                        canvas.config(bg=color)
                        background_var.config(bg=color)

                tk.Button(
                    frame,
                    text="Выбрать",
                    command=lambda v=var, c=color_canvas, e=entry: choose_color(v, c, e)
                ).grid(row=inner_row, column=3, padx=5, pady=5)

            elif prop_name == "shape":
                tk.Label(frame, text="Форма:").grid(row=inner_row, column=0, padx=5, pady=5, sticky="w")
                shape_var = tk.StringVar(value=default_value)
                shape_menu = tk.OptionMenu(frame, shape_var, *shape_options)
                shape_menu.grid(row=inner_row, column=1, columnspan=2, padx=5, pady=5)
                vars_dict[f"{category}_{prop_name}"] = shape_var

            inner_row += 1

        row_index += 1

    connection_frame = tk.LabelFrame(dialog, text="Настройка стилей соединений")
    connection_frame.grid(row=row_index // 2, column=row_index % 2, padx=10, pady=10, sticky="w")
    connection_vars = {}
    connection_canvases = {}
    connection_entries = {}
    connection_styles = {}
    connection_colors = ["refs", "includes", "extends"]

    connection_descriptions = {
        "refs": "Ссылки на узлы",
        "includes": "Узел включения",
        "extends": "Узел расширения"
    }

    for idx, connection_type in enumerate(connection_colors):
        default_color = default_connection_colors[connection_type]["color"]
        default_style = default_connection_colors[connection_type]["dashed"]

        connection_var = tk.StringVar(value=default_color)
        connection_vars[connection_type] = connection_var

        style_var = tk.StringVar(value=dashed_options[default_style])
        connection_styles[connection_type] = style_var

        tk.Label(
            connection_frame,
            text=f"{connection_descriptions[connection_type]}:"
        ).grid(row=idx * 2, column=0, padx=5, pady=5, sticky="w")

        connection_entry = tk.Entry(connection_frame, textvariable=connection_var)
        connection_entry.grid(row=idx * 2, column=1, padx=5, pady=5)
        connection_entries[connection_type] = connection_entry

        connection_canvas = tk.Canvas(connection_frame, width=20, height=20, bg=default_color, highlightthickness=1, highlightbackground="black")
        connection_canvas.grid(row=idx * 2, column=2, padx=5, pady=5)
        connection_canvases[connection_type] = connection_canvas

        tk.Button(
            connection_frame,
            text="Выбрать",
            command=lambda ct=connection_type: choose_color(
                connection_vars[ct],
                connection_canvases[ct],
                connection_entries[ct]
            )
        ).grid(row=idx * 2, column=3, padx=5, pady=5)

        tk.Label(connection_frame, text="Стиль линии:").grid(
            row=idx * 2 + 1, column=0, padx=5, pady=5, sticky="w"
        )

        dashed_values = {v: k for k, v in dashed_options.items()}
        style_menu = tk.OptionMenu(connection_frame, style_var, *dashed_options.values())
        style_menu.grid(row=idx * 2 + 1, column=1, padx=5, pady=5)

    row_index += len(connection_colors) * 2

    def reset_to_defaults():
        for reset_category, reset_props in parameters.items():
            for reset_prop_name, reset_default_value in reset_props.items():
                var_name = f"{reset_category}_{reset_prop_name}"
                vars_dict[var_name].set(reset_default_value)
                if reset_prop_name.endswith("color"):
                    canvases_dict[var_name].config(bg=reset_default_value)

        for reset_connection_type in connection_colors:
            reset_default_color = default_connection_colors[reset_connection_type]["color"]
            reset_default_style = dashed_options[default_connection_colors[reset_connection_type]["dashed"]]

            connection_vars[reset_connection_type].set(reset_default_color)
            connection_styles[reset_connection_type].set(reset_default_style)
            connection_canvases[reset_connection_type].config(bg=reset_default_color)

    reset_button = tk.Button(dialog, text="Сбросить к значениям по умолчанию", command=reset_to_defaults)
    reset_button.grid(row=row_index // 2 + 1, column=0, columnspan=2, pady=10)

    def on_ok():
        color_results = tuple(vars_dict[color_var].get() for color_var in vars_dict)
        connection_results = tuple(connection_vars[ct].get() for ct in connection_colors)
        style_results = tuple(dashed_values[connection_styles[ct].get()] for ct in connection_colors)
        dialog.result = (*color_results, *connection_results, *style_results)
        dialog.destroy()

    ok_button = tk.Button(dialog, text="Далее", command=on_ok)
    ok_button.grid(row=row_index // 2 + 2, column=0, columnspan=2, pady=10)

    dialog.wait_window()
    return getattr(dialog, "result", None)

def detect_delimiter(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()

    if ";" in first_line:
        return ";"
    elif "," in first_line:
        return ","
    else:
        result = messagebox.askyesno("Несоответствие разделителя",
                                     "По умолчанию разделитель ; Не удалось определить разделитель строк в файле. Хотите ввести свой разделитель?")
        if not result:
            return None

        delimiter = simpledialog.askstring("Разделитель", "Введите символ-разделитель:", initialvalue=";")
        if not delimiter or len(delimiter) != 1:
            messagebox.showerror("Ошибка", "Разделитель не был указан или неверный. Программа завершена")
            return None

        return delimiter

def process_data(
    input_file, output_file, nodespacing, levelspacing, edgespacing, width, height, padding,
    topic_fill, topic_stroke, topic_shape,
    db_fill, db_stroke, db_shape,
    folder_fill, folder_stroke, folder_shape,
    service_fill, service_stroke, service_shape,
    api_fill, api_stroke, api_shape,
    column_order,
    refs_color, includes_color, extends_color,
    refs_style, includes_style, extends_style
):
    delimiter = detect_delimiter(input_file)
    if delimiter is None:
        print("Разделитель не был указан. Программа завершена")
        return

    services = set()
    consumer_topics = defaultdict(set)
    producer_topics = defaultdict(set)
    db_readers = defaultdict(set)
    db_writers = defaultdict(set)
    folder_readers = defaultdict(set)
    folder_writers = defaultdict(set)
    api_callers = defaultdict(set)
    api_called_by = defaultdict(set)
    topic_consumers = defaultdict(set)
    db_producers = defaultdict(set)
    folder_producers = defaultdict(set)
    api_producers = defaultdict(set)
    service_urls = {}

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter)
            headers = next(reader)

            if len(headers) < 10:  # Проверяем количество колонок
                messagebox.showerror("Ошибка", "Файл содержит неверные заголовки. Программа завершена")
                return

            # Определяем индексы колонок
            source_idx = column_order.index("Сервисы")
            consumes_topic_idx = column_order.index("Топики чтения")
            produces_topic_idx = column_order.index("Топики записи")
            reads_db_idx = column_order.index("БД чтения")
            writes_db_idx = column_order.index("БД записи")
            reads_folder_idx = column_order.index("Папки чтения")
            writes_folder_idx = column_order.index("Папки записи")
            calls_api_idx = column_order.index("API вызов")
            called_by_api_idx = column_order.index("API запрос")

            try:
                service_url_idx = column_order.index("Ссылки на сервисы")
            except ValueError:
                service_url_idx = None

            for row in reader:
                source = row[source_idx].strip() if source_idx < len(row) else ""
                consumes_topic = row[consumes_topic_idx].strip() if consumes_topic_idx < len(row) else ""
                produces_topic = row[produces_topic_idx].strip() if produces_topic_idx < len(row) else ""
                reads_db = row[reads_db_idx].strip() if reads_db_idx < len(row) else ""
                writes_db = row[writes_db_idx].strip() if writes_db_idx < len(row) else ""
                reads_folder = row[reads_folder_idx].strip() if reads_folder_idx < len(row) else ""
                writes_folder = row[writes_folder_idx].strip() if writes_folder_idx < len(row) else ""
                calls_api = row[calls_api_idx].strip() if calls_api_idx < len(row) else ""
                called_by_api = row[called_by_api_idx].strip() if called_by_api_idx < len(row) else ""
                service_url = row[service_url_idx].strip() if service_url_idx is not None and service_url_idx < len(row) else ""

                if not source:
                    print(f"Отсутствует сервис в строке: {row}")
                    continue

                services.add(source)
                service_urls[source] = service_url

                if consumes_topic:
                    consumer_topics[source].add(consumes_topic)
                    topic_consumers[consumes_topic].add(source)

                if produces_topic:
                    producer_topics[source].add(produces_topic)

                if reads_db:
                    db_readers[source].add(reads_db)

                if writes_db:
                    db_writers[source].add(writes_db)
                    db_producers[reads_db].add(source)

                if reads_folder:
                    folder_readers[source].add(reads_folder)

                if writes_folder:
                    folder_writers[source].add(writes_folder)
                    folder_producers[reads_folder].add(source)

                if calls_api:
                    api_callers[source].add(calls_api)
                    api_producers[calls_api].add(source)

                if called_by_api:
                    api_called_by[source].add(called_by_api)

    except FileNotFoundError:
        print(f"Файл '{input_file}' не найден")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return

    headerCSV.write_csv_file_headers(output_file, width, height, padding, nodespacing, levelspacing, edgespacing, refs_color, includes_color, extends_color,
                                     refs_style, includes_style, extends_style)

    with open(output_file, 'a', encoding='utf-8') as file:

        id_counter = 1
        topic_id_map = {}
        db_id_map = {}
        folder_id_map = {}
        service_id_map = {service: id_counter + idx for idx, service in enumerate(sorted(services)) if service.strip()}
        api_id_map = {}

        all_topics = set()
        for topics in consumer_topics.values():
            all_topics.update(topics)
        for topics in producer_topics.values():
            all_topics.update(topics)

        all_dbs = set()
        for dbs in db_readers.values():
            all_dbs.update(dbs)
        for dbs in db_writers.values():
            all_dbs.update(dbs)

        all_folders = set()
        for folders in folder_readers.values():
            all_folders.update(folders)
        for folders in folder_writers.values():
            all_folders.update(folders)

        all_apis = set()
        for apis in api_callers.values():
            all_apis.update(apis)
        for apis in api_called_by.values():
            all_apis.update(apis)

        # Создание узлов для микросервисов
        for service in sorted(services):
            service_id_map[service] = id_counter
            id_counter += 1

        # Создание узлов для топиков
        for topic in sorted(all_topics):
            topic_id_map[topic] = id_counter

            consumer_services = [
                str(service_id_map[service])
                for service in topic_consumers[topic]
                if service in service_id_map
            ]
            includes_str = f'"{",".join(consumer_services)}"' if consumer_services else ""

            file.write(f"{id_counter},{topic},{topic_fill},{topic_stroke},{topic_shape},{includes_str},,\n")
            id_counter += 1

        # Создание узлов для баз данных
        for db in sorted(all_dbs):
            db_id_map[db] = id_counter

            consumer_services = [
                str(service_id_map[service])
                for service in db_readers.keys()
                if db in db_readers[service]
            ]
            includes_str = f'"{",".join(consumer_services)}"' if consumer_services else ""

            file.write(f"{id_counter},{db},{db_fill},{db_stroke},{db_shape},{includes_str},,\n")
            id_counter += 1

        # Создание узлов для папок
        for folder in sorted(all_folders):
            folder_id_map[folder] = id_counter

            consumer_services = [
                str(service_id_map[service])
                for service in folder_readers.keys()
                if folder in folder_readers[service]
            ]
            includes_str = f'"{",".join(consumer_services)}"' if consumer_services else ""

            file.write(f"{id_counter},{folder},{folder_fill},{folder_stroke},{folder_shape},{includes_str},,\n")
            id_counter += 1

        # Создание узлов для API
        for api in sorted(all_apis):
            api_id_map[api] = id_counter

            consumer_services = [
                str(service_id_map[service])
                for service in api_called_by.keys()
                if api in api_called_by[service]
            ]
            includes_str = f'"{",".join(consumer_services)}"' if consumer_services else ""

            file.write(f"{id_counter},{api},{api_fill},{api_stroke},{api_shape},{includes_str},,\n")
            id_counter += 1

        # Создание связей для микросервисов
        for service in sorted(services):
            service_id = service_id_map[service]

            produce_topics = [
                str(topic_id_map[topic])
                for topic in producer_topics.get(service, [])
                if topic in topic_id_map
            ]
            write_dbs = [
                str(db_id_map[db])
                for db in db_writers.get(service, [])
                if db in db_id_map
            ]
            write_folders = [
                str(folder_id_map[folder])
                for folder in folder_writers.get(service, [])
                if folder in folder_id_map
            ]
            call_apis = [
                str(api_id_map[api])
                for api in api_callers.get(service, [])
                if api in api_id_map
            ]

            extends_str = f'"{",".join(produce_topics + write_dbs + write_folders + call_apis)}"' if produce_topics or write_dbs or write_folders or call_apis else ""

            service_url = service_urls.get(service, "")

            file.write(f"{service_id},{service},{service_fill},{service_stroke},{service_shape},,{extends_str},,{service_url}\n")

    print(f"CSV-файл успешно создан: {output_file}")

def main():
    root = tk.Tk()
    root.withdraw()

    # Загрузка настроек из файла
    settings = load_settings()

    show_about_window()

    input_file, output_file, column_order, use_default_size, use_default_color = get_column_order(settings)

    if not input_file or not output_file:
        print("Не выбраны файлы. Программа завершена")
        return

    if len(column_order) != 10 or set(column_order) != set(settings["default_column_order"]):
        print("Неверный порядок колонок. Программа завершена")
        return

    if not use_default_size:
        size_parameters = get_size_parameters(settings)
        if size_parameters is None:
            print("Параметры размеров не были введены. Программа завершена")
            return
    else:
        size_parameters = tuple(settings["default_size_parameters"].values())

    if not use_default_color:
        color_parameters = get_color_parameters(settings)
        if color_parameters is None:
            print("Параметры цвета и формы не были введены. Программа завершена")
            return
    else:
        color_parameters = (
            settings["default_color_parameters"]["topic"]["fill_color"],
            settings["default_color_parameters"]["topic"]["stroke_color"],
            settings["default_color_parameters"]["topic"]["shape"],
            settings["default_color_parameters"]["db"]["fill_color"],
            settings["default_color_parameters"]["db"]["stroke_color"],
            settings["default_color_parameters"]["db"]["shape"],
            settings["default_color_parameters"]["folder"]["fill_color"],
            settings["default_color_parameters"]["folder"]["stroke_color"],
            settings["default_color_parameters"]["folder"]["shape"],
            settings["default_color_parameters"]["service"]["fill_color"],
            settings["default_color_parameters"]["service"]["stroke_color"],
            settings["default_color_parameters"]["service"]["shape"],
            settings["default_color_parameters"]["api"]["fill_color"],
            settings["default_color_parameters"]["api"]["stroke_color"],
            settings["default_color_parameters"]["api"]["shape"],
            settings["default_connection_colors"]["refs"]["color"],
            settings["default_connection_colors"]["includes"]["color"],
            settings["default_connection_colors"]["extends"]["color"],
            settings["default_connection_colors"]["refs"]["dashed"],
            settings["default_connection_colors"]["includes"]["dashed"],
            settings["default_connection_colors"]["extends"]["dashed"]
        )

    process_data(
        input_file, output_file,
        *size_parameters,
        *color_parameters[:15],
        column_order,
        *color_parameters[15:18],
        *color_parameters[18:]
    )

if __name__ == "__main__":
    main()