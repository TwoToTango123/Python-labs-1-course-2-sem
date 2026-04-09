# Лабораторная работа №2: Модель задачи, дескрипторы и @property

## Цель
Освоить управление доступом к атрибутам и защиту инвариантов доменной модели задачи.

## Что реализовано
- Доменная модель Task с инкапсуляцией и строгой валидацией состояния.
- Пользовательские data descriptors для полей:
	- id;
	- description;
	- priority;
	- status;
	- created_at.
- Вычисляемые свойства через @property:
	- is_ready_for_execution;
	- is_done.
- Контроль корректных переходов статусов и предотвращение некорректных состояний.
- Специализированные исключения для нарушения инвариантов.
- Демонстрация различий между data и non-data descriptors.
- Аннотации типов и документация во всех ключевых модулях.

## Публичный API
- Task, TaskStatus.
- collect_tasks, collect_tasks_from_source.
- TaskSourceProtocol.
- Ошибки предметной области:
	- TaskError;
	- TaskValidationError;
	- TaskStateTransitionError;
	- InvalidTaskIdError;
	- InvalidTaskDescriptionError;
	- InvalidTaskPriorityError;
	- InvalidTaskStatusError;
	- InvalidTaskCreatedAtError.

## Структура проекта
- src/task_platform/task_types.py: доменная модель Task, descriptors, @property, сериализация.
- src/task_platform/exceptions.py: специализированные исключения.
- src/task_platform/runtime_validation.py: нормализация входных словарей в Task.
- src/task_platform/contracts.py: протокол источника задач.
- src/task_platform/intake.py: агрегирование задач из нескольких источников.
- src/task_platform/sources/: файловый, генераторный и API-stub источники.
- tests/: unit-тесты модели, инвариантов, источников, контрактов и runtime-валидации.

## Требования
- Python 3.11+
- pytest
- pytest-cov

## Запуск демо
```bash
.venv\Scripts\python.exe demo.py
```

В демонстрации показано:
1. Валидация модели Task и переходы статусов.
2. Отличие data/non-data descriptor.
3. Работа всех источников задач и общего intake.
4. Сериализация и восстановление Task через to_dict/from_dict.

## Запуск тестов
```bash
.venv\Scripts\python.exe -m pytest
```

## Проверка покрытия
```bash
.venv\Scripts\python.exe -m pytest --cov=src/task_platform --cov-report=term-missing --cov-fail-under=80
```

## Запуск через Docker
```bash
docker build -t lab2 .
docker run --rm lab2
```

При запуске контейнера выполняются:
1. demo.py.
2. pytest с отчётом о покрытии.
