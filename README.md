# Лабораторная работа №3: Очередь задач, итераторы и генераторы

## Цель
Освоить реализацию пользовательских коллекций, протоколов итерации и ленивую обработку данных через генераторы.

## Что реализовано

### 1. Класс TaskQueue с полной поддержкой протокола итерации
- **`__iter__()`** — создаёт новый итератор для каждого вызова
- **`__next__()`** — автоматически через встроенный iter()
- **Множественный обход** — одна очередь может быть обойдена несколько раз
- **Совместимость** с `for`, `list()`, `sum()` и другими стандартными конструкциями Python

### 2. Ленивые фильтры через генераторы (не создают копии в памяти)
- **`filter_by_status(*statuses)`** — фильтрация по одному или нескольким статусам
- **`filter_by_priority(min_priority, max_priority)`** — фильтрация по диапазону приоритета
- **`filter_by_status_and_priority()`** — комбинированная фильтрация
- **`filter(predicate)`** — универсальный фильтр с пользовательским условием

### 3. Трансформации данных
- **`map(transform)`** — ленивое преобразование каждой задачи
- **`flatten(selector)`** — развёртывание вложенных коллекций
- **`chunk(size)`** — ленивое разбиение на группы
- **`take(n)`** — отбор первых n элементов
- **`skip(n)`** — пропуск первых n элементов
- **`sorted_by(key, reverse)`** — сортировка (создаёт новую TaskQueue)

### 4. Эффективность и оптимизация памяти
- Все фильтры используют генераторы для памятно-эффективной обработки
- Поддержка работы с очень большими объёмами задач (тысячи без перегрузки памяти)
- Корректная обработка StopIteration
- Отсутствие избыточного хранения данных

## Публичный API
```python
from task_platform import TaskQueue, Task, TaskStatus

# Создание очереди
queue = TaskQueue([task1, task2, task3])

# Итерация
for task in queue:
    print(task)

# Ленивая фильтрация
ready = queue.filter_by_status(TaskStatus.READY)
high_priority = queue.filter_by_priority(min_priority=7)

# Трансформации
ids = queue.map(lambda t: t.id)
batches = queue.chunk(10)

# Совместимость
total_priority = sum(queue.map(lambda t: t.priority))
list_of_tasks = list(queue)
```

## Структура проекта
```
src/task_platform/
├── task_queue.py           ✨ НОВОЕ: очередь с итераторами и генераторами
├── task_types.py           доменная модель Task
├── contracts.py            протокол TaskSourceProtocol
├── exceptions.py           специализированные исключения
├── intake.py               агрегирование задач
├── runtime_validation.py   нормализация данных
└── sources/
    ├── file_source.py
    ├── generator_source.py
    └── api_stub_source.py

tests/
├── test_task_queue.py      ✨ НОВОЕ: полное покрытие TaskQueue (210+ тестов)
├── test_task_model.py      tests модели Task
├── test_contracts.py       tests протоколов
└── ...

demo.py                     ✨ ОБНОВЛЕНО: демо для Lab3
```

## Примеры использования

### Итерация и стандартные конструкции
```python
queue = TaskQueue([task1, task2, task3])

# Использование в for цикле
for task in queue:
    print(task.id)

# Повторный обход - возможен
list(queue)  # Вторая итерация - работает

# Совместимость со стандартными функциями
sum(queue.map(lambda t: t.priority))
```

### Ленивая фильтрация
```python
# По статусу
ready_tasks = queue.filter_by_status(TaskStatus.READY)

# По приоритету
high_priority = queue.filter_by_priority(min_priority=7)

# Комбинированная
critical_ready = queue.filter_by_status_and_priority(
    statuses=[TaskStatus.READY],
    min_priority=8
)

# Универсальная
custom = queue.filter(lambda t: t.is_ready_for_execution and t.priority > 5)
```

### Трансформации и обработка
```python
# Извлечение ID
ids = list(queue.map(lambda t: t.id))

# Пакетная обработка
for batch in queue.chunk(10):
    process_batch(batch)

# Отбор и пропуск
top_5 = list(queue.take(5))
rest = list(queue.skip(5))

# Сортировка (создаёт новую очередь)
by_priority = queue.sorted_by(lambda t: t.priority)
by_priority_desc = queue.sorted_by(lambda t: t.priority, reverse=True)
```

### Аналитика и агрегирование
```python
# Подсчёт задач по статусам
stats = {}
for status in TaskStatus:
    count = sum(1 for _ in queue.filter_by_status(status))
    stats[status.value] = count

# Средний приоритет
avg_priority = sum(queue.map(lambda t: t.priority)) / len(queue)

# Цепочка операций
critical_ids = [
    t.id for t in queue.filter(
        lambda t: t.priority >= 8 and t.status == TaskStatus.READY
    )
]
```

## Требования
- Python 3.11+
- pytest
- pytest-cov

## Запуск демо
```bash
.venv\Scripts\python.exe demo.py
```

В демонстрации показано:
1. Протокол итерации и множественный обход
2. Совместимость со стандартными конструкциями Python
3. Ленивые фильтры (по статусу, приоритету, комбинированные)
4. Трансформации (map, chunk, take, skip, sorted_by)
5. Эффективность на больших объёмах (1000+ задач)
6. Генераторы и отсутствие избыточного использования памяти

## Запуск тестов
```bash
.venv\Scripts\python.exe -m pytest tests/test_task_queue.py -v
```

Тесты включают:
- Протокол итерации (__iter__, __next__, StopIteration)
- Длину и булеву логику (__len__, __bool__)
- Фильтрацию по статусу и приоритету
- Комбинированную фильтрацию
- Универсальные фильтры с predicate
- Трансформации (map, chunk, take, skip, sorted_by)
- Цепочки операций (chaining)
- Граничные случаи (пустые очереди, большие объёмы)
- Интеграционные тесты (реальные use-cases)

## Проверка покрытия
```bash
.venv\Scripts\python.exe -m pytest tests/ --cov=src/task_platform --cov-report=term-missing --cov-fail-under=80
```

## Запуск через Docker
```bash
docker build -t lab3 .
docker run --rm lab3
```

При запуске контейнера выполняются:
1. demo.py
2. pytest с отчётом о покрытии

## Критерии оценки
- **Корректность итераторов (40%)** — полная поддержка протокола, множественный обход
- **Использование генераторов (30%)** — ленивая оценка, отсутствие копий в памяти
- **Эффективность решения (20%)** — работа с большими объёмами, оптимизация памяти
- **Документация и структура кода (10%)** — docstring, type hints, примеры
