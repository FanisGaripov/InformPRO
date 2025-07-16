# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, session, request, Response, stream_with_context
import g4f
from random import randint
import json
import logging
import os


app = Flask(__name__)
'''В планах: Главная, Онлайн-компилятор, Чат-бот, Теория: Python,
sql, ip, криптобезопасность, ИИ, идеи пет-проектов, Экзамены: огэ, егэ, Генерация задач,
Обо мне'''

'''Выполнено: Главная, Онлайн-компилятор, чат-бот, обо мне, идеи пет-проектов, Теория: Python; Экзамены: огэ, егэ; генерация задач'''

'''Осталось: Теория: sql, ip, криптобезопасность, ИИ'''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/online-compiler')
def online_compiler():
    return render_template('online_compiler.html')


@app.route('/programming-chatbot', methods=['GET', 'POST'])
def programming_chatbot():
    # страница с чат-ботом
    return render_template('programming_chatbot.html')


@app.route('/stream')
def stream():
    question = request.args.get('question')
    response = ask_physics_question(question)
    return Response(stream_with_context(response_stream(response)), content_type='text/event-stream')


def response_stream(response):
    for chunk in response:
        if isinstance(chunk, str):
            yield f"data: {chunk}\n\n"


def ask_physics_question(question):
    """Функция для отправки вопроса ИИ и получения ответа с потоковым выводом."""
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",  # Модель ИИ
            messages=[{"role": "system", "content": "Ты помощник, который отвечает только на вопросы по информатике ЕГЭ. экзаменам, вопросы напрямую связанные с информатикой, программированием. Если это другая тема, отвечай так: Это тема не относится к информатике или программированию, задайте другой вопрос."},
                      {"role": "user", "content": question}],
            stream=True  # Включаем потоковый вывод
        )
        for chunk in response:
            if isinstance(chunk, str):
                yield chunk
    except Exception as e:
        yield f"Произошла ошибка: {e}"


@app.route('/theory')
def theory():
    return render_template('theory.html')


@app.route('/theory/python')
def python_theory():
    return render_template('python_theory.html')


@app.route('/theory/sql')
def sql_theory():
    return render_template('sql_theory.html')


@app.route('/theory/ip')
def ip_theory():
    return render_template('ip_theory.html')


@app.route('/theory/cryptosecurity')
def cryptosecurity_theory():
    return render_template('cryptosecurity_theory.html')


@app.route('/theory/ai')
def ai_theory():
    return render_template('ai.html')


@app.route('/pet-projects')
def pet_projects():
    return render_template('pet_projects.html')


def load_tasks_from_files(number):
    catalog = {}
    if number == 1:
        tasks_dir = 'База заданий ОГЭ'
    else:
        tasks_dir = 'База заданий ЕГЭ'

    for filename in os.listdir(tasks_dir):
        if filename.startswith('tasks_type_') and filename.endswith('.json'):
            theme = filename.replace('tasks_type_', '').replace('.json', '')
            try:
                with open(os.path.join(tasks_dir, filename), 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                    catalog[theme] = tasks
            except Exception as e:
                print(f"Ошибка загрузки файла {filename}: {e}")

    return catalog


oge_catalog = load_tasks_from_files(1)
ege_catalog = load_tasks_from_files(2)
PRETTY_CATEGORY_NAMES_OGE = {
    # Раздел 1. Цифровая грамотность
    "11_Файлы_и_папки_каталоги_Принципы_построения_файл": "1.1 Файлы и папки (каталоги). Принципы построения файловых систем.",
    "12_Объединение_компьютеров_в_сеть_Сеть_Интернет_Ве": "1.2 Объединение компьютеров в сеть. Сеть Интернет. Веб-страница, веб-сайт.",

    # Раздел 2. Теоретические основы информатики
    "21_Дискретность_данных_Возможность_описания_непрер": "2.1 Дискретность данных. Возможность описания непрерывных объектов и процессов с помощью дискретных данных.",
    "22_Информационный_объём_данных_Бит_минимальная_еди": "2.2 Информационный объём данных. Бит – минимальная единица количества информации – двоичный разряд.",
    "27_Логические_высказывания_Логические_значения_выс": "2.7 Логические высказывания. Логические значения высказываний.",
    "28_Логические_элементы_Знакомство_с_логическими_ос": "2.8 Логические элементы. Знакомство с логическими основами компьютера",
    "211_Граф_Вершина_ребро_путь_Ориентированные_и_неор": "2.11 Граф. Вершина, ребро, путь. Ориентированные и неориентированные графы.",

    # Раздел 3. Алгоритмы и программирование
    "31_Свойства_алгоритма_Способы_записи_алгоритма_сло": "3.1 Свойства алгоритма. Способы записи алгоритма (словесный, в виде блок-схемы, программа).",
    "32_Язык_программирования_Python_C_Паскаль_Java_C_Ш": "3.2 Язык программирования (Python, C++, Паскаль, Java, C#, Школьный Алгоритмический Язык).",
    "34_Определение_возможных_результатов_работы_алгори": "3.4 Определение возможных результатов работы алгоритма при данном множестве входных данных.",

    # Раздел 4. Информационные технологии
    "41_Текстовые_документы_и_их_структурные_элементы_с": "4.1 Текстовые документы и их структурные элементы (страница, абзац, строка, слово, символ).",
    "43_Подготовка_мультимедийных_презентаций_Слайд_Доб": "4.3 Подготовка мультимедийных презентаций. Слайд.",
    "45_Условные_вычисления_в_электронных_таблицах_Сумм": "4.5 Условные вычисления в электронных таблицах.",
}
PRETTY_CATEGORY_NAMES_EGE = {
    # Раздел 1. Цифровая грамотность
    "11_Основные_тенденции_развития_компьютерных_технол": "1.1 Основные тенденции развития компьютерных технологий.",
    "12_Принципы_построения_и_аппаратные_компоненты_ком": "1.2 Принципы построения и аппаратные компоненты компьютерных сетей.",
    "14_Скорость_передачи_данных_Зависимость_времени_пе": "1.4 Скорость передачи данных.",

    # Раздел 2. Теоретические основы информатики
    "21_Двоичное_кодирование_Равномерные_и_неравномерны": "2.1 Двоичное кодирование",
    "22_Теоретические_подходы_к_оценке_количества_инфор": "2.2 Теоретические подходы к оценке количества информации.",
    "23_Системы_счисления_Развёрнутая_запись_целых_и_др": "2.3 Системы счисления.",
    "26_Кодирование_изображений_Оценка_информационного_": "2.6 Кодирование изображений и звука",
    "27_Алгебра_логики_Понятие_высказывания_Высказывате": "2.7 Алгебра логики. Понятие высказывания.",
    "210_Модели_и_моделирование_Цели_моделирования_Адек": "2.10 Модели и моделирование. Цели моделирования.",
    "211_Представление_целых_чисел_в_памяти_компьютера_": "2.11 Представление целых чисел в памяти компьютера.",
    "213_Графы_Основные_понятия_Виды_графов_Описание_гр": "2.13 Графы. Основные понятия. Виды графов.",
    "215_Дискретные_игры_двух_игроков_с_полной_информац": "2.15 Дискретные игры двух игроков с полной информацией.",

    # Раздел 3. Алгоритмы и программирование
    "31_Формализация_понятия_алгоритма_Машина_Тьюринга_": "3.1 Формализация понятия алгоритма. Машина Тьюринга как универсальная модель вычислений.",
    "32_Оценка_сложности_вычислений_Время_работы_и_объё": "3.2 Оценка сложности вычислений.",
    "33_Определение_возможных_результатов_работы_просте": "3.3 Определение возможных результатов работы простейших алгоритмов управления исполнителями и вычислительных алгоритмов.",
    "34_Алгоритмы_обработки_натуральных_чисел_записанны": "3.4 Алгоритмы обработки натуральных чисел, записанных в позиционных системах счисления.",
    "37_Рекурсия_Рекурсивные_процедуры_и_функции_Исполь": "3.7 Рекурсия. Рекурсивные процедуры и функции.",
    "39_Обработка_символьных_данных_Встроенные_функции_": "3.9 Обработка символьных данных. Встроенные функции языка программирования для обработки символьных строк.",
    "310_Массивы_и_последовательности_чисел_Вычисление_": "3.10 Массивы и последовательности чисел.",

    # Раздел 4. Информационные технологии
    "42_Анализ_данных_с_помощью_электронных_таблиц_Вычи": "4.2 Анализ данных с помощью электронных таблиц.",
    "45_Табличные_реляционные_базы_данных_Таблица_предс": "4.5 Табличные (реляционные) базы данных.",
    "46_Текстовый_процессор_Средства_поиска_и_автозамен": "4.6 Текстовый процессор. Средства поиска и автозамены в текстовом процессоре.",
}


@app.route('/exams')
def exams():
    return render_template('exams.html')


@app.route('/exams/oge')
def oge():
    return render_template('oge_catalog.html')


@app.route('/exams/ege')
def ege():
    return render_template('ege_catalog.html')


@app.route('/exams/ege/<category>')
def EGE_tasks(category):
    # задания егэ
    tasks = ege_catalog.get(category, [])
    pretty_category = PRETTY_CATEGORY_NAMES_EGE.get(category, category.replace('_', ' '))
    return render_template('ege_tasks.html', category=pretty_category, tasks=tasks)


@app.route('/exams/oge/<category>')
def OGE_tasks(category):
    # задания огэ
    tasks = oge_catalog.get(category, [])
    pretty_category = PRETTY_CATEGORY_NAMES_OGE.get(category, category.replace('_', ' '))
    return render_template('oge_tasks.html', category=pretty_category, tasks=tasks)


def generate_problems(difficulty, num_problems, topics=None):
    """
    Генерирует задачи по программированию на Python в формате JSON
    с использованием модели GPT через g4f.

    Параметры:
    - difficulty (str): сложность задач ('легкая', 'средняя', 'сложная', 'олимпиадная')
    - num_problems (int): количество задач для генерации
    - topics (list, optional): список тем для задач (например, ['строки', 'математика', 'графы'])
    """

    system_prompt = f"""
Твоя роль - создавать качественные задачи по программированию на Python разного уровня сложности.
Пользователь указывает сложность задач и количество. Задачи могут быть как школьного уровня, так и олимпиадными.

Требования:

1. Сложность задач должна соответствовать указанной пользователем:
   - 'легкая': базовые задачи на условные операторы, циклы, простые алгоритмы
   - 'средняя': задачи на рекурсию, обработку строк, математические алгоритмы
   - 'сложная': продвинутые алгоритмы, оптимизация, комбинаторика
   - 'олимпиадная': нестандартные задачи, требующие креативного подхода

2. Формат каждой задачи:
    - Название (отражает суть задачи)
    - Условие (четкое и понятное описание)
    - Примеры входных/выходных данных (если применимо)
    - Решение (чистый и эффективный Python код)
    - Тестовые случаи (10 штук с разными сценариями)

3. Технические требования:
   - Используй только стандартную библиотеку Python
   - Код должен быть читаемым с правильными отступами
   - Для сложных задач добавляй комментарии в решении
   - Тестовые случаи должны покрывать разные сценарии

4. Дополнительно:
   - Если указаны темы ({topics}), учитывай их при генерации
   - Задачи должны быть оригинальными и интересными
   - Для олимпиадных задач предлагай неочевидные решения

Пример выходных данных (JSON):
{{
    "задачи": [
        {{
            "название": "Поиск простых чисел-близнецов",
            "сложность": "средняя",
            "условие": "Напишите программу, которая находит все пары простых чисел-близнецов в диапазоне от 1 до N...",
            "примеры": "Ввод: 20\nВывод: (3, 5), (5, 7), (11, 13), (17, 19)",
            "решение": "def find_twin_primes(n):\n    # Реализация алгоритма...",
            "тесты": [
                {{"ввод": "10", "вывод": "(3, 5), (5, 7)"}},
                {{"ввод": "20", "вывод": "(3, 5), (5, 7), (11, 13), (17, 19)"}},
                ... # всего 10 тестов
            ]
        }}
    ]
}}

Убери mark-down разметку и не пиши ```json

"""

    user_prompt = {
        "сложность": difficulty,
        "количество_задач": num_problems,
        "темы": topics if topics else ["любые"]
    }

    try:
        response = g4f.ChatCompletion.create(
            model="deepseek-v3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)}
            ],
            stream=False
        )

        # Обработка ответа
        problems = json.loads(response)
        return problems

    except json.JSONDecodeError as e:
        logging.error(f"Ошибка декодирования JSON: {str(e)}")
        return {"ошибка": "Неверный формат ответа", "ответ": response}

    except Exception as e:
        logging.error(f"Ошибка API: {str(e)}")
        return {"ошибка": "Не удалось сгенерировать задачи"}


@app.route('/task-generation', methods=['GET', 'POST'])
def task_generator():
    result = ''
    task_condition = ''
    task_tests = []
    lvl = ''

    if request.method == 'POST':
        lvl = request.form.get('lvl')
        result = generate_problems(
            difficulty=lvl,
            num_problems=1,
            topics=None
        )

        # Извлекаем данные из результата
        if isinstance(result, dict) and 'задачи' in result:
            first_task = result['задачи'][0]
            task_condition = first_task.get('условие', '')
            task_tests = first_task.get('тесты', [])

    return render_template(
        'task_generator.html',
        lvl=lvl,
        condition=task_condition,
        tests=task_tests,
        result=result  # передаем полностью для скрытого поля
    )


@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html')


@app.route('/aboutme/projects')
def my_projects():
    return render_template('my_projects.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)