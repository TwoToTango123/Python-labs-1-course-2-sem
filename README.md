# Лабораторная работа №4: Асинхронный исполнитель задач

## Цель
Реализовать асинхронную систему выполнения задач с расширяемыми обработчиками,
контрактами Protocol, централизованным логированием и обработкой ошибок.

## Что реализовано

1. Асинхронная очередь задач
- Используется asyncio.Queue в AsyncTaskExecutor.
- Пул worker-потоков на базе asyncio.create_task.
- Методы submit(), wait_until_idle() и run() для полного жизненного цикла.

2. Контракт обработчика через Protocol
- AsyncTaskHandlerProtocol в contracts.py:
  async метод handle(task: Task) -> str.
- Регистрация обработчиков через register_handler(name, handler, matcher).

3. Контекстные менеджеры для ресурсов
- Executor реализует async context manager (__aenter__/__aexit__).
- Обработчики могут быть async context manager и автоматически открываются/закрываются.
- Для этого используется AsyncExitStack.

4. Централизованное логирование и обработка ошибок
- Логи жизненного цикла исполнителя и каждой задачи.
- Ошибки задачи не падают процесс целиком: сохраняются в TaskExecutionResult.
- Ведется агрегированная статистика: total/succeeded/failed.

5. Расширяемая архитектура
- Новые обработчики добавляются без правок ядра исполнителя.
- Маршрутизация задач задается matcher-функциями.
- Поддержаны стандартные обработчики: SleepTaskHandler и FailingTaskHandler.

## Ключевые модули
```
src/task_platform/
├── async_execution.py   # AsyncTaskExecutor, TaskExecutionResult, статистика
├── handlers.py          # Базовый async handler + примеры обработчиков
├── contracts.py         # TaskSourceProtocol + AsyncTaskHandlerProtocol
├── exceptions.py        # Ошибки исполнения и маршрутизации
├── task_types.py        # Доменная модель Task
└── ...
```

## Запуск локально
```bash
.venv\Scripts\python.exe demo.py
```

Демонстрация показывает:
1. Формирование входных задач.
2. Асинхронный запуск с несколькими worker.
3. Маршрутизацию в разные обработчики.
4. Обработку ошибки в одном из обработчиков.
5. Итоговые статусы задач и статистику.

## Тесты
```bash
.venv\Scripts\python.exe -m pytest
```

## Запуск через Docker
```bash
docker build -t lab4-async-executor .
docker run --rm lab4-async-executor
```

Что увидит преподаватель в выводе контейнера:
1. Подробный вывод demo.py (очередь, обработчики, успехи и ошибки).
2. Затем запуск pytest с покрытием.

## Технические требования ЛР4: покрытие
1. async/await: используется во всех этапах исполнения задач.
2. Без блокировок event loop: применяются asyncio.Queue и asyncio.sleep (без time.sleep).
3. Расширяемость: обработчики подключаются через register_handler + matcher.
4. Аннотации и документация: type hints и docstring в публичных компонентах.
