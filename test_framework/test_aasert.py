# coding=utf-8
import pytest
from uatf import *


def assert_fail(f):
    def wrapper(*args, **kwargs):
        result = False
        try:
            f(*args, **kwargs)
        except (AssertionError, TypeError):
            result = True
        finally:
            if not result:
                raise Exception(args[2])

    return wrapper


assert_not_that = assert_fail(assert_that)


class TestInAndNotIn(TestCase):

    @pytest.mark.parametrize("arg1,arg2,_is_in", (
            ['1', '12', True],
            ['3', '12', False],
            ['123' * 100, '123' * 200, True],
            ['12' * 100, '123' * 200, False]
    ))
    def test_in_string(self, arg1, arg2, _is_in):
        """Проверка матчера IN. Строки"""

        if _is_in:
            assert_that(arg1, is_in(arg2), 'Строка входит!')
        else:
            assert_not_that(arg1, is_in(arg2), 'Строка не должна входить!')

    @pytest.mark.parametrize("arg1,arg2,_is_in", (
            [1, [1, 2, 3], True],
            [4, [1, 2, 3], False],
            [[1, 2], [[1, 2], [3, 4]], True],
            [[1, 2], [1, 2, 3], False],
            [[3, 4], [1, 2, 3], False]
    ))
    def test_in_list(self, arg1, arg2, _is_in):
        """Проверка матчера IN. Списки"""

        if _is_in:
            assert_that(arg1, is_in(arg2), 'Вхождение верное')
        else:
            assert_not_that(arg1, is_in(arg2), 'Вхождение не верное')

    @pytest.mark.parametrize("arg1,arg2,_is_in", (
            [1, {1: 2}, True],
            ['a', {'a': 2}, True],
            [2, {1: 2}, False],
            ['b', {'a': 2}, False]
    ))
    def test_in_dict(self, arg1, arg2, _is_in):
        """Проверка матчера IN. Словари"""

        if _is_in:
            assert_that(arg1, is_in(arg2), 'Верное вхождение')
        else:
            assert_not_that(arg1, is_in(arg2), 'Не верное вхождение')

    @pytest.mark.parametrize("arg1,arg2,_is_in", (
            ['Аб', 'аБf', True],
            ['гш', 'ГШf', True],
            ['б', 'b', False]
    ))
    def test_is_in_ignoring_case(self, arg1, arg2, _is_in):
        """Проверка матчера IN. Словари"""

        if _is_in:
            assert_that(arg1, is_in_ignoring_case(arg2), 'Верное вхождение')
        else:
            assert_not_that(arg1, is_in_ignoring_case(arg2), 'Не верное вхождение')

    @pytest.mark.parametrize("arg1,arg2,_is_in", (
            ['Аб', 'аБ', True],
            ['гш', 'ГШ', True],
            ['б', 'b', False]
    ))
    def test_equal_to_ignoring_case(self, arg1, arg2, _is_in):
        """Проверка матчера IN. Словари"""

        if _is_in:
            assert_that(arg1, equal_to_ignoring_case(arg2), 'Верное вхождение')
        else:
            assert_not_that(arg1, equal_to_ignoring_case(arg2), 'Не верное вхождение')

    @pytest.mark.parametrize("arg1,arg2,_is_not_in", (
            ['12' * 100, '123' * 200, True],
            ['1', '12', False],
            ['3', '12', True],
            ['123' * 100, '123' * 200, False]
    ))
    def test_not_in_short_string(self, arg1, arg2, _is_not_in):
        """Проверка матчера IN. Строки"""

        if _is_not_in:
            assert_that(arg1, is_not_in(arg2), 'Не должно входить')
        else:
            assert_not_that(arg1, is_not_in(arg2), 'Верное вхождение')

    @pytest.mark.parametrize("arg1,arg2,_is_not_in", (
            [4, [1, 2, 3], True],
            [[1, 2], [1, 2, 3], True],
            [[3, 4], [1, 2, 3], True],
            [1, [1, 2, 3], False]
    ))
    def test_not_in_list(self, arg1, arg2, _is_not_in):
        """Проверка матчера IN. Списки"""

        if _is_not_in:
            assert_that(arg1, is_not_in(arg2), 'Не должно входить')
        else:
            assert_not_that(arg1, is_not_in(arg2), 'Должно входить')

    @pytest.mark.parametrize("arg1,arg2,_is_not_in", (
            [1, {1: 2}, False],
            ['a', {'a': 2}, False],
            [2, {1: 2}, True],
            ['b', {'a': 2}, True]
    ))
    def test_not_in_dict(self, arg1, arg2, _is_not_in):
        """Проверка матчера IN. Списки"""

        if _is_not_in:
            assert_that(arg1, is_not_in(arg2), 'Не должно входить')
        else:
            assert_not_that(arg1, is_not_in(arg2), 'Должно входить')


class TestLess(TestCase):

    @pytest.mark.parametrize("arg1,arg2,matcher", (
            ['a', 12, less_than],
            [12, '12', less_than],
            ['a', 12, less_than_or_equal_to],
            [12, '12', less_than_or_equal_to],
    ))
    def test_less_greater_than_wrong_types(self, arg1, arg2, matcher):
        """Проверка матчеры для неверных типов"""

        assert_not_that(arg1, matcher(arg2), 'Не верное равенство')

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            ['a', 'a', False],
            ['12', '12', False],
            ['12' * 300, '12' * 300, False],
            ['12', '21', True],
            ['12', '123', True],
            ['12' * 299, '12' * 300, True],
            ['a', 'а', True],  # разные языки
            ['21', '12', False],
            [5, 6, True],
            [-1, -3, False],
            [6, 5, False],
            [-3, -1, True]
    ))
    def test_less(self, arg1, arg2, _equal):
        """Проверка матчера less_than. Числа, Строки"""

        if _equal:
            assert_that(arg1, less_than(arg2), 'Верное неравество')
        else:
            assert_not_that(arg1, less_than(arg2), 'Неверное неравенство')

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            ['a', 'a', True],
            ['12', '12', True],
            ['12' * 300, '12' * 300, True],
            ['12', '21', True],
            ['12', '123', True],
            ['12' * 299, '12' * 300, True],
            ['a', 'а', True],  # разные языки
            ['21', '12', False],
            [5, 6, True],
            [-1, -3, False],
            [6, 5, False],
            [-3, -1, True],
            [5, 5, True]
    ))
    def test_less_than_or_equal_to(self, arg1, arg2, _equal):
        """Проверка матчера less_than. Числа, Строки"""

        if _equal:
            assert_that(arg1, less_than_or_equal_to(arg2), 'Верное неравество')
        else:
            assert_not_that(arg1, less_than_or_equal_to(arg2), 'Неверное неравенство')


class TestGreater(TestCase):

    @pytest.mark.parametrize("arg1,arg2,matcher", (
            ['a', 12, greater_than],
            [12, '12', greater_than],
            ['a', 12, greater_than_or_equal_to],
            [12, '12', greater_than_or_equal_to]
    ))
    def test_greater_than_wrong_types(self, arg1, arg2, matcher):
        """Проверка матчеры для неверных типов"""

        assert_not_that(arg1, matcher(arg2), 'Не верное равенство')

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            ['a', 'a', False],
            ['12', '12', False],
            ['12' * 300, '12' * 300, False],
            ['12', '21', False],
            ['12', '123', False],
            ['12' * 299, '12' * 300, False],
            ['a', 'а', False],  # разные языки
            ['21', '12', True],
            [5, 6, False],
            [-1, -3, True],
            [6, 5, True],
            [-3, -1, False]
    ))
    def test_greater(self, arg1, arg2, _equal):
        """Проверка матчера greater_than_or_equal_to. Числа, Строки"""

        if _equal:
            assert_that(arg1, greater_than(arg2), 'Верное неравество')
        else:
            assert_not_that(arg1, greater_than(arg2), 'Неверное неравенство')

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            ['a', 'a', True],
            ['12', '12', True],
            ['12' * 300, '12' * 300, True],
            ['12', '21', False],
            ['12', '123', False],
            ['12' * 299, '12' * 300, False],
            ['a', 'а', False],  # разные языки
            ['21', '12', True],
            [5, 6, False],
            [-1, -3, True],
            [6, 5, True],
            [-3, -1, False],
            [5, 5, True]
    ))
    def test_greater_than_or_equal_to(self, arg1, arg2, _equal):
        """Проверка матчера greater_than_or_equal_to. Числа, Строки"""

        if _equal:
            assert_that(arg1, greater_than_or_equal_to(arg2), 'Верное неравество')
        else:
            assert_not_that(arg1, greater_than_or_equal_to(arg2), 'Неверное неравенство')


class TestEqualAndNotEqual(TestCase):

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            ['a', 'a', True],
            ['12', '12', True],
            ['12' * 200, '12' * 200, True],
            ['a', 'а', False],  # разные языки
            ['12', '21', False],
            ['12', '123', False]
    ))
    def test_equal_to_string(self, arg1, arg2, _equal):
        """Проверка матчера equal_to. Строки"""

        if _equal:
            assert_that(arg1, equal_to(arg2), 'Верное равенство')
        else:
            assert_not_that(arg1, equal_to(arg2), 'Не верное равенство')

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            [1, 1, True],
            [32.456, 32.456, True],
            [2, 22, False],
            [2.45, 2.456, False],
            [1 * 1e1000, 1 * 1e1000, True],
            [1 * 1e100, 1 * 1e101, False]
    ))
    def test_equal_to_int_and_float(self, arg1, arg2, _equal):
        """Проверка матчера equal_to. Числа"""

        if _equal:
            assert_that(arg1, equal_to(arg2), 'Верное равенство')
        else:
            assert_not_that(arg1, equal_to(arg2), "Неверное равенство")

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            [[1, 2], [1, 2], True],
            [[1, 2], [1, 2, 3], False],
            ['a', 'b', False],
            ['a', 'a', True]
    ))
    def test_equal_to_list(self, arg1, arg2, _equal):
        """Проверка матчера IN. Списки"""

        if _equal:
            assert_that(arg1, equal_to(arg2), 'Верное равенство')
        else:
            assert_not_that(arg1, equal_to(arg2), 'Неверное равенство')

    @pytest.mark.parametrize("arg1,arg2,_equal", (
            [{1: 2}, {1: 2}, True],
            [{'a': 1, 'b': 2}, {'b': 2, 'a': 1}, True],
            [{1, 2}, {1: 2}, False],
            [{1, 2}, {3: 4}, False],
            [{'a': 2, 'b': 1}, {'b': 2, 'a': 1}, False]
    ))
    def test_equal_to_dict(self, arg1, arg2, _equal):
        """Проверка матчера IN. Словари"""

        if _equal:
            assert_that(arg1, equal_to(arg2), 'Верное равенство')
        else:
            assert_not_that(arg1, equal_to(arg2), 'Неверное равенство')

    @pytest.mark.parametrize("arg1,arg2,_not_equal", (
            ['a', 'a', False],
            ['12', '12', False],
            ['12' * 200, '12' * 200, False],
            ['a', 'а', True],  # разные языки
            ['12', '21', True],
            ['12', '123', True]
    ))
    def test_not_equal_string(self, arg1, arg2, _not_equal):
        """Проверка матчера equal_to. Строки"""

        if _not_equal:
            assert_that(arg1, not_equal(arg2), 'Неверное равенство')
        else:
            assert_not_that(arg1, not_equal(arg2), 'Верное равенство')

    @pytest.mark.parametrize("arg1,arg2,_not_equal", (
            [1, 1, False],
            [32.456, 32.456, False],
            [1 * 1e1000, 1 * 1e1000, False],
            [2, 22, True],
            [2.45, 2.456, True],
            [1 * 1e100, 1 * 1e101, True]
    ))
    def test_not_equal_int_and_float(self, arg1, arg2, _not_equal):
        """Проверка матчера equal_to. Числа"""

        if _not_equal:
            assert_that(arg1, not_equal(arg2), 'Неверное равенство')
        else:
            assert_not_that(arg1, not_equal(arg2), 'Верное равенство')

    @pytest.mark.parametrize("arg1,arg2,_not_equal", (
            [[1, 2], [1, 2], False],
            ['a', 'a', False],
            [[1, 2], [1, 2, 3], True],
            ['a', 'b', True]
    ))
    def test_not_equal_list(self, arg1, arg2, _not_equal):
        """Проверка матчера IN. Списки"""

        if _not_equal:
            assert_that(arg1, not_equal(arg2), 'Неверное равенство')
        else:
            assert_not_that(arg1, not_equal(arg2), 'Верное равенство')

    @pytest.mark.parametrize("arg1,arg2,_not_equal", (
            [{1: 2}, {1: 2}, False],
            [{'a': 1, 'b': 2}, {'b': 2, 'a': 1}, False],
            [{1, 2}, {1: 2}, True],
            [{1, 2}, {3: 4}, True],
            [{'a': 2, 'b': 1}, {'b': 2, 'a': 1}, True]
    ))
    def test_not_equal_dict(self, arg1, arg2, _not_equal):
        """Проверка матчера IN. Словари"""

        if _not_equal:
            assert_that(arg1, not_equal(arg2), 'Неверное равенство')
        else:
            assert_not_that(arg1, not_equal(arg2), 'Верное равенство')
