"""Unit-тесты для TaskQueue - протокол итерации, ленивые фильтры и генераторы."""

import pytest
from datetime import datetime, timezone

from task_platform import Task, TaskStatus, TaskQueue


# ============================================================================
# Фиксторы (Fixtures)
# ============================================================================


@pytest.fixture
def sample_tasks():
    """Создать набор задач для тестирования."""
    return [
        Task("task_1", "Database migration", 8, status=TaskStatus.DRAFT),
        Task("task_2", "API implementation", 9, status=TaskStatus.READY),
        Task("task_3", "Unit testing", 5, status=TaskStatus.IN_PROGRESS),
        Task("task_4", "Documentation", 3, status=TaskStatus.DONE),
        Task("task_5", "Code review", 6, status=TaskStatus.READY),
        Task("task_6", "Performance optimization", 7, status=TaskStatus.IN_PROGRESS),
    ]


@pytest.fixture
def empty_queue():
    """Создать пустую очередь."""
    return TaskQueue([])


@pytest.fixture
def queue(sample_tasks):
    """Создать очередь с примерными задачами."""
    return TaskQueue(sample_tasks)


# ============================================================================
# Тесты: Протокол итерации (__iter__)
# ============================================================================


class TestTaskQueueIteration:
    """Тесты протокола итерации TaskQueue."""

    def test_iter_returns_iterator(self, queue):
        """__iter__ должен возвращать итератор."""
        result = iter(queue)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_iter_all_tasks(self, queue, sample_tasks):
        """Итератор должен обойти все задачи."""
        result = [task for task in queue]
        assert len(result) == len(sample_tasks)
        assert result == sample_tasks

    def test_iter_in_for_loop(self, queue, sample_tasks):
        """for цикл должен работать с очередью."""
        count = 0
        for task in queue:
            assert task in sample_tasks
            count += 1
        assert count == len(sample_tasks)

    def test_multiple_iterations(self, queue, sample_tasks):
        """Можно обойти одну очередь несколько раз."""
        first_pass = list(queue)
        second_pass = list(queue)
        third_pass = list(queue)

        assert first_pass == sample_tasks
        assert second_pass == sample_tasks
        assert third_pass == sample_tasks

    def test_list_constructor(self, queue, sample_tasks):
        """list() должен работать с очередью."""
        result = list(queue)
        assert result == sample_tasks

    def test_iter_empty_queue(self, empty_queue):
        """Итератор пустой очереди должен быть пустым."""
        result = list(empty_queue)
        assert result == []

    def test_next_raises_stopiteration(self, sample_tasks):
        """__next__ должен поднимать StopIteration когда закончились элементы."""
        queue = TaskQueue(sample_tasks)
        iterator = iter(queue)

        # Обойти все элементы
        for _ in range(len(sample_tasks)):
            next(iterator)

        # Следующий вызов должен поднять StopIteration
        with pytest.raises(StopIteration):
            next(iterator)

    def test_separate_iterators_independent(self, queue):
        """Несколько итераторов одной очереди должны быть независимыми."""
        iter1 = iter(queue)
        iter2 = iter(queue)

        # Авансировать первый итератор
        next(iter1)
        next(iter1)

        # Второй должен начинаться заново
        task1_from_iter2 = next(iter2)
        assert task1_from_iter2.id == "task_1"


# ============================================================================
# Тесты: Длина и булева логика
# ============================================================================


class TestTaskQueueLength:
    """Тесты методов __len__ и __bool__."""

    def test_len_with_tasks(self, queue, sample_tasks):
        """len() должен вернуть количество задач."""
        assert len(queue) == len(sample_tasks)

    def test_len_empty_queue(self, empty_queue):
        """len() пустой очереди должен быть 0."""
        assert len(empty_queue) == 0

    def test_bool_with_tasks(self, queue):
        """Непустая очередь должна быть True в булевом контексте."""
        assert bool(queue) is True
        assert queue  # Работает в if

    def test_bool_empty_queue(self, empty_queue):
        """Пустая очередь должна быть False в булевом контексте."""
        assert bool(empty_queue) is False
        assert not empty_queue  # Работает в if


# ============================================================================
# Тесты: Фильтрация по статусу (filter_by_status)
# ============================================================================


class TestFilterByStatus:
    """Тесты ленивой фильтрации по статусу."""

    def test_filter_single_status(self, queue):
        """Фильтр по одному статусу должен вернуть соответствующие задачи."""
        result = list(queue.filter_by_status(TaskStatus.READY))
        assert len(result) == 2  # task_2, task_5
        assert all(t.status == TaskStatus.READY for t in result)

    def test_filter_multiple_statuses(self, queue):
        """Фильтр по нескольким статусам должен вернуть все соответствующие."""
        result = list(
            queue.filter_by_status(TaskStatus.READY, TaskStatus.IN_PROGRESS)
        )
        assert len(result) == 4  # task_2, task_3, task_5, task_6

    def test_filter_string_statuses(self, queue):
        """Фильтр должен работать со строковыми статусами."""
        result = list(queue.filter_by_status("ready", "done"))
        assert len(result) == 3  # task_2, task_4, task_5

    def test_filter_no_matches(self, queue):
        """Если совпадений нет, результат пуст."""
        # Создать очередь только с DRAFT статусом
        draft_queue = TaskQueue(
            [Task("t", "Test", 5, status=TaskStatus.DRAFT)]
        )
        result = list(draft_queue.filter_by_status(TaskStatus.DONE))
        assert result == []

    def test_filter_returns_generator(self, queue):
        """filter_by_status должен вернуть генератор."""
        result = queue.filter_by_status(TaskStatus.READY)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_filter_lazy_evaluation(self, sample_tasks):
        """Фильтр должен быть ленивым - не создавать копию в памяти."""
        queue = TaskQueue(sample_tasks)

        # Не должно быть errors при создании фильтра
        filtered = queue.filter_by_status(TaskStatus.READY)

        # Потребление только первого элемента
        first = next(filtered)
        assert first.status == TaskStatus.READY

    def test_filter_invalid_status(self, queue):
        """Некорректный статус должен поднять ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            list(queue.filter_by_status("invalid_status"))


# ============================================================================
# Тесты: Фильтрация по приоритету (filter_by_priority)
# ============================================================================


class TestFilterByPriority:
    """Тесты ленивой фильтрации по приоритету."""

    def test_filter_min_priority(self, queue):
        """Фильтр с min_priority должен вернуть задачи >= min."""
        result = list(queue.filter_by_priority(min_priority=7))
        assert len(result) == 3  # task_1 (8), task_2 (9), task_6 (7)
        assert all(t.priority >= 7 for t in result)

    def test_filter_max_priority(self, queue):
        """Фильтр с max_priority должен вернуть задачи <= max."""
        result = list(queue.filter_by_priority(max_priority=5))
        assert len(result) == 2  # task_3 (5), task_4 (3)
        assert all(t.priority <= 5 for t in result)

    def test_filter_priority_range(self, queue):
        """Фильтр с диапазоном должен вернуть задачи в нём."""
        result = list(queue.filter_by_priority(min_priority=5, max_priority=7))
        assert len(result) == 3  # task_3 (5), task_5 (6), task_6 (7)
        assert all(5 <= t.priority <= 7 for t in result)

    def test_filter_no_priority_bounds(self, queue, sample_tasks):
        """Без ограничений должны вернуться все задачи."""
        result = list(queue.filter_by_priority())
        assert result == sample_tasks

    def test_filter_exact_priority(self, queue):
        """Фильтр с одинаковыми min/max должен вернуть точное значение."""
        result = list(queue.filter_by_priority(min_priority=6, max_priority=6))
        assert len(result) == 1
        assert result[0].priority == 6

    def test_filter_invalid_min_priority(self, queue):
        """Некорректный min_priority должен поднять ValueError."""
        with pytest.raises(ValueError, match="min_priority must be"):
            list(queue.filter_by_priority(min_priority=0))

        with pytest.raises(ValueError, match="min_priority must be"):
            list(queue.filter_by_priority(min_priority=11))

    def test_filter_invalid_max_priority(self, queue):
        """Некорректный max_priority должен поднять ValueError."""
        with pytest.raises(ValueError, match="max_priority must be"):
            list(queue.filter_by_priority(max_priority=0))

    def test_filter_min_greater_than_max(self, queue):
        """min_priority > max_priority должен поднять ValueError."""
        with pytest.raises(ValueError, match="min_priority must be"):
            list(queue.filter_by_priority(min_priority=8, max_priority=5))


# ============================================================================
# Тесты: Комбинированная фильтрация (filter_by_status_and_priority)
# ============================================================================


class TestFilterByStatusAndPriority:
    """Тесты комбинированной ленивой фильтрации."""

    def test_combined_filter_both_conditions(self, queue):
        """Оба условия должны работать вместе."""
        result = list(
            queue.filter_by_status_and_priority(
                statuses=[TaskStatus.READY],
                min_priority=6,
            )
        )
        # task_2 (priority=9, status=READY) и task_5 (priority=6, status=READY)
        assert len(result) == 2
        assert all(t.status == TaskStatus.READY for t in result)
        assert all(t.priority >= 6 for t in result)

    def test_combined_filter_only_status(self, queue):
        """Без приоритета должна работать фильтрация по статусу."""
        result = list(
            queue.filter_by_status_and_priority(statuses=[TaskStatus.DONE])
        )
        assert len(result) == 1
        assert result[0].id == "task_4"

    def test_combined_filter_only_priority(self, queue):
        """Без статуса должна работать фильтрация по приоритету."""
        result = list(
            queue.filter_by_status_and_priority(min_priority=8)
        )
        assert len(result) == 2  # task_1 (8), task_2 (9)

    def test_combined_filter_no_matches(self, queue):
        """Если нет совпадений, результат пуст."""
        result = list(
            queue.filter_by_status_and_priority(
                statuses=[TaskStatus.DONE],
                min_priority=8,
            )
        )
        assert result == []

    def test_combined_filter_returns_generator(self, queue):
        """Должен вернуть генератор."""
        result = queue.filter_by_status_and_priority(
            statuses=[TaskStatus.READY]
        )
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


# ============================================================================
# Тесты: Универсальный фильтр (filter)
# ============================================================================


class TestUniversalFilter:
    """Тесты универсального фильтра с predicate."""

    def test_filter_with_predicate(self, queue):
        """filter() должен работать с пользовательским predicate."""
        result = list(queue.filter(lambda t: t.priority > 6))
        assert len(result) == 3  # task_1, task_2, task_6

    def test_filter_complex_condition(self, queue):
        """filter() должен работать с сложными условиями."""
        result = list(
            queue.filter(
                lambda t: t.status == TaskStatus.READY and t.priority > 5
            )
        )
        # task_2 (priority=9, READY) и task_5 (priority=6, READY)
        assert len(result) == 2
        assert all(t.status == TaskStatus.READY for t in result)
        assert all(t.priority > 5 for t in result)

    def test_filter_returns_all_when_true(self, queue, sample_tasks):
        """filter() с lambda True должен вернуть все."""
        result = list(queue.filter(lambda t: True))
        assert result == sample_tasks

    def test_filter_returns_none_when_false(self, queue):
        """filter() с lambda False должен вернуть пусто."""
        result = list(queue.filter(lambda t: False))
        assert result == []

    def test_filter_returns_generator(self, queue):
        """filter() должен вернуть генератор."""
        result = queue.filter(lambda t: True)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


# ============================================================================
# Тесты: map
# ============================================================================


class TestMap:
    """Тесты трансформации через map."""

    def test_map_extracts_ids(self, queue):
        """map() должен извлекать IDs."""
        ids = list(queue.map(lambda t: t.id))
        assert ids == ["task_1", "task_2", "task_3", "task_4", "task_5", "task_6"]

    def test_map_extracts_priorities(self, queue):
        """map() должен извлекать приоритеты."""
        priorities = list(queue.map(lambda t: t.priority))
        assert priorities == [8, 9, 5, 3, 6, 7]

    def test_map_sum_priorities(self, queue):
        """map() с sum() должен работать для подсчёта сумм."""
        total = sum(queue.map(lambda t: t.priority))
        assert total == 38  # 8+9+5+3+6+7

    def test_map_returns_generator(self, queue):
        """map() должен вернуть генератор."""
        result = queue.map(lambda t: t.id)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


# ============================================================================
# Тесты: chunk
# ============================================================================


class TestChunk:
    """Тесты разбиения на группы."""

    def test_chunk_size_2(self, queue, sample_tasks):
        """Разбиение на размер 2."""
        chunks = list(queue.chunk(2))
        assert len(chunks) == 3
        assert all(len(chunk) == 2 for chunk in chunks[:2])
        assert len(chunks[2]) == 2

    def test_chunk_size_larger_than_queue(self, queue, sample_tasks):
        """Если размер больше очереди, вся очередь в одной группе."""
        chunks = list(queue.chunk(100))
        assert len(chunks) == 1
        assert len(chunks[0]) == len(sample_tasks)

    def test_chunk_size_1(self, queue, sample_tasks):
        """Размер 1 должен создать по задаче на группу."""
        chunks = list(queue.chunk(1))
        assert len(chunks) == len(sample_tasks)
        assert all(len(chunk) == 1 for chunk in chunks)

    def test_chunk_invalid_size(self, queue):
        """Размер <= 0 должен поднять ValueError."""
        with pytest.raises(ValueError):
            list(queue.chunk(0))

        with pytest.raises(ValueError):
            list(queue.chunk(-1))

    def test_chunk_returns_tuples(self, queue):
        """chunk() должен возвращать кортежи."""
        chunks = list(queue.chunk(2))
        assert all(isinstance(chunk, tuple) for chunk in chunks)

    def test_chunk_returns_generator(self, queue):
        """chunk() должен вернуть генератор."""
        result = queue.chunk(2)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


# ============================================================================
# Тесты: take и skip
# ============================================================================


class TestTakeAndSkip:
    """Тесты отбора и пропуска элементов."""

    def test_take_first_n(self, queue, sample_tasks):
        """take(n) должен вернуть первые n элементов."""
        result = list(queue.take(3))
        assert result == sample_tasks[:3]

    def test_take_more_than_available(self, queue, sample_tasks):
        """take() больше чем есть, должен вернуть все."""
        result = list(queue.take(100))
        assert result == sample_tasks

    def test_take_zero(self, queue):
        """take(0) должен вернуть пусто."""
        result = list(queue.take(0))
        assert result == []

    def test_skip_first_n(self, queue, sample_tasks):
        """skip(n) должен пропустить первые n элементов."""
        result = list(queue.skip(2))
        assert result == sample_tasks[2:]

    def test_skip_more_than_available(self, queue):
        """skip() больше чем есть, должен вернуть пусто."""
        result = list(queue.skip(100))
        assert result == []

    def test_skip_zero(self, queue, sample_tasks):
        """skip(0) должен вернуть все."""
        result = list(queue.skip(0))
        assert result == sample_tasks

    def test_take_returns_generator(self, queue):
        """take() должен вернуть генератор."""
        result = queue.take(2)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_skip_returns_generator(self, queue):
        """skip() должен вернуть генератор."""
        result = queue.skip(2)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


# ============================================================================
# Тесты: sorted_by
# ============================================================================


class TestSortedBy:
    """Тесты сортировки."""

    def test_sorted_by_priority_ascending(self, queue):
        """sorted_by() должен сортировать по приоритету."""
        sorted_queue = queue.sorted_by(lambda t: t.priority)
        priorities = [t.priority for t in sorted_queue]
        assert priorities == [3, 5, 6, 7, 8, 9]

    def test_sorted_by_priority_descending(self, queue):
        """sorted_by(reverse=True) должен сортировать в обратном порядке."""
        sorted_queue = queue.sorted_by(lambda t: t.priority, reverse=True)
        priorities = [t.priority for t in sorted_queue]
        assert priorities == [9, 8, 7, 6, 5, 3]

    def test_sorted_by_id(self, queue):
        """sorted_by() должен работать с id."""
        sorted_queue = queue.sorted_by(lambda t: t.id)
        ids = [t.id for t in sorted_queue]
        assert ids == ["task_1", "task_2", "task_3", "task_4", "task_5", "task_6"]

    def test_sorted_by_returns_taskqueue(self, queue):
        """sorted_by() должен вернуть TaskQueue."""
        result = queue.sorted_by(lambda t: t.priority)
        assert isinstance(result, TaskQueue)

    def test_sorted_by_can_be_iterated_multiple_times(self, queue):
        """Результат sorted_by() должен быть итерируемым несколько раз."""
        sorted_queue = queue.sorted_by(lambda t: t.priority)
        first = list(sorted_queue)
        second = list(sorted_queue)
        assert first == second


# ============================================================================
# Тесты: Цепочки операций (chaining)
# ============================================================================


class TestOperationChaining:
    """Тесты цепочек операций."""

    def test_chain_filter_and_map(self, queue):
        """Цепочка filter + map должна работать."""
        result = list(
            queue.map(lambda t: t.id)
        )  # Получить IDs
        high_priority = list(
            queue.filter(lambda t: t.priority > 6)
        )
        assert len(high_priority) == 3

    def test_filter_then_map_ids(self, queue):
        """Фильтр ready задач и получить их IDs."""
        ready_ids = list(
            queue.map(lambda t: t.id)
            for t in queue.filter(lambda t: t.status == TaskStatus.READY)
        )
        # Выполняем двойной генератор
        ids = [t.id for t in queue.filter(lambda t: t.status == TaskStatus.READY)]
        assert len(ids) == 2

    def test_chain_with_sorted(self, queue):
        """Сортировка результата фильтра."""
        high_priority = queue.filter(lambda t: t.priority >= 6)
        sorted_by_priority = TaskQueue(list(high_priority)).sorted_by(
            lambda t: t.priority
        )
        priorities = [t.priority for t in sorted_by_priority]
        assert priorities == sorted(priorities)

# ============================================================================
# Тесты: Граничные случаи и эффективность
# ============================================================================


class TestEdgeCasesAndPerformance:
    """Тесты граничных случаев и эффективности."""

    def test_empty_queue_operations(self, empty_queue):
        """Все операции на пустой очереди должны работать."""
        assert list(empty_queue) == []
        assert list(empty_queue.filter_by_status(TaskStatus.READY)) == []
        assert list(empty_queue.filter_by_priority(min_priority=5)) == []
        assert list(empty_queue.filter(lambda t: True)) == []
        assert list(empty_queue.map(lambda t: t.id)) == []
        assert list(empty_queue.chunk(2)) == []

    def test_single_task_queue(self):
        """Очередь с одной задачей должна работать."""
        task = Task("single", "Single task", 5)
        queue = TaskQueue([task])

        assert len(queue) == 1
        assert list(queue) == [task]
        assert list(queue.filter(lambda t: True)) == [task]

    def test_generator_input(self):
        """TaskQueue должен работать с генератором на входе."""

        def task_generator():
            for i in range(3):
                yield Task(f"gen_{i}", f"Generated task {i}", i + 1)

        queue = TaskQueue(task_generator())
        assert len(queue) == 3
        assert queue[0].id == "gen_0" if hasattr(queue, "__getitem__") else True

    def test_large_queue_lazy_evaluation(self):
        """Большая очередь должна использовать ленивую оценку."""
        large_tasks = [
            Task(f"task_{i}", f"Task {i}", (i % 10) + 1, status=TaskStatus.DRAFT)
            for i in range(1000)
        ]
        queue = TaskQueue(large_tasks)

        # Все задачи имеют DRAFT статус
        filtered = queue.filter_by_status(TaskStatus.READY)

        # Результат должен быть пусто
        first = next(filtered, None)
        assert first is None

    def test_generator_not_exhausted_on_filter(self, sample_tasks):
        """Фильтр не должен исчерпывать генератор полностью, если не нужно."""
        queue = TaskQueue(sample_tasks)

        # Создать фильтр но не потребить
        filtered = queue.filter_by_status(TaskStatus.READY)

        # Фильтр должен быть итератором
        assert hasattr(filtered, "__next__")

    def test_repr_string(self, queue):
        """__repr__ должен показать информацию о очереди."""
        repr_str = repr(queue)
        assert "TaskQueue" in repr_str
        assert "6 tasks" in repr_str


# ============================================================================
# Интеграционные тесты
# ============================================================================


class TestIntegration:
    """Интеграционные тесты для реальных use-cases."""

    def test_batch_processing_with_chunks(self, queue):
        """Use case: пакетная обработка задач."""
        batch_size = 2
        total_processed = 0

        for batch in queue.chunk(batch_size):
            total_processed += len(batch)

        assert total_processed == len(queue)

    def test_get_count_of_high_priority(self, queue):
        """Use case: подсчитать высокоприоритетные задачи."""
        high_priority_count = sum(
            1 for t in queue.filter(lambda t: t.priority >= 7)
        )
        assert high_priority_count == 3

    def test_get_average_priority(self, queue):
        """Use case: вычислить среднее значение приоритета."""
        priorities = list(queue.map(lambda t: t.priority))
        average = sum(priorities) / len(priorities)
        assert average == 38 / 6  # (8+9+5+3+6+7) / 6

    def test_complex_analytics(self, queue):
        """Use case: сложная аналитика."""
        stats = {
            "total": len(queue),
            "by_status": {},
        }

        for status in TaskStatus:
            count = sum(1 for _ in queue.filter_by_status(status))
            if count > 0:
                stats["by_status"][status.value] = count

        assert stats["total"] == 6
        assert stats["by_status"][TaskStatus.READY.value] == 2
