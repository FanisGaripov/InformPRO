# крч, это парсер для fipi. в данном случае парсер написан(переделан под егэ). Чтобы обрабатывать огэ, нужно всего лишь в нескольких местах поменять ссылки и proj=...
import requests
from bs4 import BeautifulSoup
import time
import json
import os
import re

BASE_URL = "https://ege.fipi.ru/bank/"
QUESTIONS_URL = BASE_URL + "questions.php"
INIT_URL = BASE_URL + "index.php?proj=B9ACA5BBB2E19E434CD6BEC25284C67F"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})
response = session.get(INIT_URL, verify=False)
response.raise_for_status()

params = {
    'proj': 'B9ACA5BBB2E19E434CD6BEC25284C67F',
    'search': '1',
    'pagesize': '50',
    'theme': '',
    'qkind': '',
    'qlevel': '',
    'qsstruct': '',
    'qpos': '',
    'qid': '',
    'zid': '',
    'solved': '',
    'favorite': '',
    'blind': ''
}

tasks = []
page = 0
has_more = True
max_attempts = 3  # Максимальное количество попыток при ошибке
retry_delay = 5  # Задержка между попытками в секундах
max_empty_pages = 3  # Максимальное количество пустых страниц подряд
empty_pages_count = 0  # Счетчик пустых страниц

print("Начинаем сбор заданий...")
while has_more and empty_pages_count < max_empty_pages:
    print(f"Обрабатываю страницу {page + 1}...")
    params['page'] = str(page)

    for attempt in range(max_attempts):
        try:
            response = session.post(QUESTIONS_URL, data=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            task_elements = soup.find_all('div', class_='qblock')

            # Если нет заданий и это первая страница - возможно ошибка
            if not task_elements and page == 0:
                raise ValueError("Не найдено ни одного задания на первой странице")

            current_page_tasks = 0
            for task in task_elements:
                try:
                    task_id = task.get('id')[1:]
                    div_with_type_and_topic = soup.find('div', id=f'i{task_id}')
                    task_type = task.select_one('div.hint').get_text()
                    task_text = task.find('table').get_text()
                    script_text = task.find('script', string=re.compile('ShowPictureQ'))
                    match = re.search(r"ShowPictureQ\('(.+?)'\)", str(script_text))
                    if match is not None:
                        relative_path = match.group(1)
                        task_image = f'https://ege.fipi.ru/{relative_path}'
                    else:
                        task_image = None
                    task_topic = div_with_type_and_topic.find('td', class_='param-row').get_text()

                    tasks.append({
                        'id': task_id,
                        'type': task_type,
                        'text': task_text,
                        'image': task_image,
                        'topic': task_topic,
                        'page': page + 1
                    })
                    current_page_tasks += 1
                except Exception as task_error:
                    print(f"Ошибка при обработке задания: {task_error}")
                    continue

            print(f"Добавлено {current_page_tasks} заданий со страницы {page + 1}")

            # Если на странице нет заданий, увеличиваем счетчик пустых страниц
            if current_page_tasks == 0:
                empty_pages_count += 1
                print(f"Пустая страница. Счетчик пустых страниц: {empty_pages_count}/{max_empty_pages}")
            else:
                empty_pages_count = 0  # Сбрасываем счетчик, если нашли задания

            # Переходим на следующую страницу независимо от количества заданий
            page += 1
            time.sleep(1 + attempt)  # Увеличиваем задержку после каждой попытки

            break  # Выходим из цикла попыток, если успешно

        except Exception as e:
            print(f"Ошибка при обработке страницы {page + 1} (попытка {attempt + 1}): {str(e)}")
            if attempt == max_attempts - 1:
                has_more = False
                print("Превышено максимальное количество попыток. Завершаем сбор.")
                break
            time.sleep(retry_delay * (attempt + 1))  # Увеличиваем задержку при повторных попытках

# Сохраняем результаты
output_file = 'fipi_tasks.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"Сбор завершен. Сохранено {len(tasks)} заданий в файл {output_file}")


def clean_filename(text):
    # Заменяем все не-буквенно-цифровые символы на подчеркивания
    cleaned = re.sub(r'[^\w\s-]', '', text.strip())
    # Заменяем пробелы на подчеркивания
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    # Укорачиваем слишком длинные имена
    return cleaned[:50]  # Ограничиваем длину имени файла


with open('fipi_tasks.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
tasks_by_type = {}
for task in tasks:
    task_type = task['topic']
    if task_type not in tasks_by_type:
        tasks_by_type[task_type] = []
    tasks_by_type[task_type].append(task)

for task_type, type_tasks in tasks_by_type.items():
    safe_name = clean_filename(task_type)
    filename = f'tasks_type_{safe_name}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(type_tasks, f, ensure_ascii=False, indent=2)

print(f"Задания отсортированы по {len(tasks_by_type)} типам")