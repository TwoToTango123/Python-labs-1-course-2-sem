"""Очередь задач с поддержкой итерации, фильтрации и ленивой обработки."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar, overload

from .task_types import Task, TaskStatus

T = TypeVar("T")


class TaskQueue:
    """Очередь задач с поддержкой протокола итерации и ленивой фильтрации.

    Особенности:
    - Полная поддержка протокола итерации (__iter__, __next__)
    - Возможность множественного обхода очереди
    - Ленивые фильтры через генераторы (не создают копии в памяти)
    - Совместимость с стандартными конструкциями Python (for, list, sum)
    - Эффективная обработка больших объёмов задач

    Example:
        >>> tasks = [Task("1", "Task 1", 5), Task("2", "Task 2", 3)]
        >>> queue = TaskQueue(tasks)
        >>> for task in queue:
        ...     print(task.id)
        1
        2
        >>> list(queue)  # Повторный обход
        [Task(...), Task(...)]
        >>> high_priority = queue.filter_by_priority(min_priority=7)
        >>> list(high_priority)  # Ленивая фильтрация
        []
    """

    def __init__(self, tasks: Iterable[Task]) -> None:
        """Инициализировать очередь задач.

        Args:
            tasks: Итерируемая последовательность задач.
                  Может быть список, генератор или другой итерируемый объект.

        Note:
            Внутренне хранит задачи в виде кортежа для гарантии
            неизменяемости и возможности переиспользования итератора.
        """
        self._tasks: tuple[Task, ...] = tuple(tasks)

    def __iter__(self) -> Iterator[Task]:
        """Вернуть итератор для обхода очереди.

        Returns:
            Iterator[Task]: Новый итератор с начала очереди.

        Note:
            Каждый вызов создаёт новый итератор, позволяя
            множественный обход одной и той же очереди.

        Example:
            >>> queue = TaskQueue([task1, task2])
            >>> list(queue)  # Первый обход
            >>> list(queue)  # Второй обход - работает
        """
        return iter(self._tasks)

    def __len__(self) -> int:
        """Вернуть количество задач в очереди.

        Returns:
            int: Количество задач.

        Example:
            >>> queue = TaskQueue([task1, task2, task3])
            >>> len(queue)
            3
        """
        return len(self._tasks)

    def __bool__(self) -> bool:
        """Проверить наличие задач в очереди.

        Returns:
            bool: True если очередь не пуста, иначе False.

        Example:
            >>> empty_queue = TaskQueue([])
            >>> bool(empty_queue)
            False
            >>> queue = TaskQueue([task1])
            >>> bool(queue)
            True
        """
        return len(self._tasks) > 0

    def __repr__(self) -> str:
        """Строковое представление очереди для отладки.

        Returns:
            str: Представление в виде TaskQueue(...).
        """
        return f"TaskQueue({len(self._tasks)} tasks)"

    def filter_by_status(self, *statuses: TaskStatus | str) -> Iterator[Task]:
        """Ленивый фильтр задач по статусам.

        Использует генератор для памятно-эффективной фильтрации.
        Не создаёт копию очереди в памяти.

        Args:
            *statuses: Один или несколько статусов для фильтрации.
                      Могут быть TaskStatus или строки.

        Yields:
            Task: Задачи с указанными статусами.

        Raises:
            ValueError: Если передан некорректный статус.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> ready_tasks = queue.filter_by_status(TaskStatus.READY)
            >>> for task in ready_tasks:
            ...     print(task.id)
            >>> # Или несколько статусов
            >>> active = queue.filter_by_status(
            ...     TaskStatus.READY,
            ...     TaskStatus.IN_PROGRESS
            ... )
        """
        # Нормализовать статусы в TaskStatus
        parsed_statuses = self._parse_statuses(statuses)

        for task in self._tasks:
            if task.status in parsed_statuses:
                yield task

    def filter_by_priority(
        self,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> Iterator[Task]:
        """Ленивый фильтр задач по диапазону приоритета.

        Использует генератор для памятно-эффективной фильтрации.
        Не создаёт копию очереди в памяти.

        Args:
            min_priority: Минимальный приоритет (включительно).
                         Если None, нет нижнего ограничения.
            max_priority: Максимальный приоритет (включительно).
                         Если None, нет верхнего ограничения.

        Yields:
            Task: Задачи в указанном диапазоне приоритетов.

        Raises:
            ValueError: Если приоритеты некорректны (не в диапазоне 1-10
                       или min > max).

        Example:
            >>> queue = TaskQueue(tasks)
            >>> high_priority = queue.filter_by_priority(min_priority=7)
            >>> for task in high_priority:
            ...     print(task.priority)
            8
            9
            >>> medium = queue.filter_by_priority(min_priority=5, max_priority=7)
        """
        # Валидация приоритетов
        self._validate_priority_range(min_priority, max_priority)

        for task in self._tasks:
            if self._in_priority_range(task.priority, min_priority, max_priority):
                yield task

    def filter_by_status_and_priority(
        self,
        statuses: Iterable[TaskStatus | str] | None = None,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> Iterator[Task]:
        """Комбинированный ленивый фильтр по статусу и приоритету.

        Комбинирует оба фильтра для оптимизации обхода очереди.
        Проходит по очереди только один раз.

        Args:
            statuses: Статусы для фильтрации. Если None, все статусы подходят.
            min_priority: Минимальный приоритет (включительно).
            max_priority: Максимальный приоритет (включительно).

        Yields:
            Task: Задачи, удовлетворяющие обоим условиям.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> # Только готовые задачи высокого приоритета
            >>> result = queue.filter_by_status_and_priority(
            ...     statuses=[TaskStatus.READY],
            ...     min_priority=7
            ... )
        """
        parsed_statuses = (
            self._parse_statuses(statuses) if statuses else None
        )
        self._validate_priority_range(min_priority, max_priority)

        for task in self._tasks:
            status_match = (
                parsed_statuses is None or task.status in parsed_statuses
            )
            priority_match = self._in_priority_range(
                task.priority, min_priority, max_priority
            )

            if status_match and priority_match:
                yield task

    def filter(self, predicate: Callable[[Task], bool]) -> Iterator[Task]:
        """Универсальный ленивый фильтр с пользовательским предикатом.

        Использует генератор для памятно-эффективной фильтрации.

        Args:
            predicate: Функция-предикат, принимающая Task и возвращающая bool.

        Yields:
            Task: Задачи, для которых predicate вернул True.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> # Задачи с id, начинающимся на "task_"
            >>> result = queue.filter(lambda t: t.id.startswith("task_"))
            >>> # Готовые задачи с приоритетом выше 5
            >>> high_ready = queue.filter(
            ...     lambda t: t.is_ready_for_execution and t.priority > 5
            ... )
        """
        for task in self._tasks:
            if predicate(task):
                yield task

    def map(
        self,
        transform: Callable[[Task], T],
    ) -> Iterator[T]:
        """Ленивое преобразование задач через функцию трансформации.

        Использует генератор для памятно-эффективного преобразования.

        Args:
            transform: Функция для преобразования каждой задачи.

        Yields:
            T: Преобразованные значения.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> ids = queue.map(lambda t: t.id)
            >>> list(ids)
            ['task_1', 'task_2', 'task_3']
            >>> priorities = queue.map(lambda t: t.priority)
            >>> sum(priorities)  # Сумма приоритетов
            15
        """
        for task in self._tasks:
            yield transform(task)

    def flatten(
        self,
        selector: Callable[[Task], Iterable[T]],
    ) -> Iterator[T]:
        """Ленивое развёртывание (flatMap) коллекций из задач.

        Использует вложенные генераторы для памятно-эффективного
        развёртывания.

        Args:
            selector: Функция, возвращающая iterable для каждой задачи.

        Yields:
            T: Развёрнутые значения.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> # Если в задаче есть список тегов
            >>> tags = queue.flatten(lambda t: t.tags if hasattr(t, 'tags') else [])
        """
        for task in self._tasks:
            for item in selector(task):
                yield item

    def chunk(self, size: int) -> Iterator[tuple[Task, ...]]:
        """Ленивое разбиение очереди на группы (chunks) определённого размера.

        Использует генератор для памятно-эффективного разбиения.

        Args:
            size: Размер каждой группы. Должен быть > 0.

        Yields:
            tuple[Task, ...]: Группы задач размером <= size.

        Raises:
            ValueError: Если size <= 0.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> for batch in queue.chunk(10):
            ...     process_batch(batch)
        """
        if size <= 0:
            raise ValueError("chunk size must be > 0")

        for i in range(0, len(self._tasks), size):
            yield self._tasks[i : i + size]

    def take(self, n: int) -> Iterator[Task]:
        """Ленивый отбор первых n задач из очереди.

        Использует генератор для памятно-эффективного отбора.

        Args:
            n: Количество задач для отбора.

        Yields:
            Task: Первые n задач (или все задачи, если их меньше).

        Example:
            >>> queue = TaskQueue(tasks)
            >>> first_five = list(queue.take(5))
        """
        for i, task in enumerate(self._tasks):
            if i >= n:
                break
            yield task

    def skip(self, n: int) -> Iterator[Task]:
        """Ленивый пропуск первых n задач из очереди.

        Использует генератор для памятно-эффективного пропуска.

        Args:
            n: Количество задач для пропуска.

        Yields:
            Task: Все задачи, начиная с индекса n.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> after_skip = list(queue.skip(3))
        """
        for i, task in enumerate(self._tasks):
            if i >= n:
                yield task

    def sorted_by(
        self,
        key: Callable[[Task], object],
        reverse: bool = False,
    ) -> TaskQueue:
        """Ленивую сортировку с созданием новой очереди.

        Note:
            Эта операция не ленивая - требует загрузки всех данных в памяти,
            поскольку сортировка по определению требует доступа ко всем элементам.
            Результат оборачивается в новую TaskQueue для цепочки операций.

        Args:
            key: Функция для извлечения ключа сортировки из задачи.
            reverse: Сортировка в обратном порядке.

        Returns:
            TaskQueue: Новая очередь с отсортированными задачами.

        Example:
            >>> queue = TaskQueue(tasks)
            >>> by_priority = queue.sorted_by(lambda t: t.priority)
            >>> by_id_desc = queue.sorted_by(lambda t: t.id, reverse=True)
        """
        sorted_tasks = sorted(self._tasks, key=key, reverse=reverse)
        return TaskQueue(sorted_tasks)

    # ======================== Утилиты ========================

    @staticmethod
    def _parse_statuses(
        statuses: Iterable[TaskStatus | str],
    ) -> set[TaskStatus]:
        """Парсить статусы из строк или TaskStatus объектов.

        Args:
            statuses: Итерируемая последовательность статусов.

        Returns:
            set[TaskStatus]: Множество парсленных статусов.

        Raises:
            ValueError: Если какой-то статус некорректен.
        """
        parsed = set()
        for status in statuses:
            if isinstance(status, TaskStatus):
                parsed.add(status)
            elif isinstance(status, str):
                try:
                    parsed.add(TaskStatus(status))
                except ValueError as e:
                    raise ValueError(
                        f"Invalid status '{status}'. "
                        f"Must be one of: {', '.join(s.value for s in TaskStatus)}"
                    ) from e
            else:
                raise ValueError(
                    f"Status must be TaskStatus or str, got {type(status)}"
                )
        return parsed

    @staticmethod
    def _validate_priority_range(
        min_priority: int | None,
        max_priority: int | None,
    ) -> None:
        """Валидировать диапазон приоритетов.

        Args:
            min_priority: Минимальный приоритет.
            max_priority: Максимальный приоритет.

        Raises:
            ValueError: Если приоритеты некорректны.
        """
        if min_priority is not None:
            if not isinstance(min_priority, int) or min_priority < 1 or min_priority > 10:
                raise ValueError(
                    "min_priority must be an integer between 1 and 10"
                )

        if max_priority is not None:
            if not isinstance(max_priority, int) or max_priority < 1 or max_priority > 10:
                raise ValueError(
                    "max_priority must be an integer between 1 and 10"
                )

        if (
            min_priority is not None
            and max_priority is not None
            and min_priority > max_priority
        ):
            raise ValueError("min_priority must be <= max_priority")

    @staticmethod
    def _in_priority_range(
        priority: int,
        min_priority: int | None,
        max_priority: int | None,
    ) -> bool:
        """Проверить нахождение приоритета в диапазоне.

        Args:
            priority: Проверяемый приоритет.
            min_priority: Минимальное значение (включительно).
            max_priority: Максимальное значение (включительно).

        Returns:
            bool: True если приоритет в диапазоне.
        """
        if min_priority is not None and priority < min_priority:
            return False
        if max_priority is not None and priority > max_priority:
            return False
        return True
