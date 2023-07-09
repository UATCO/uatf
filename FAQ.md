# Пережитые синяки:

## PyCharm не видит фикстуры: <br>
не видит переменную окружения PYTEST_PLUGINS (см. в README)
Если задавали переменную окружения в системе, то просто надо ребутнуть компьютер, если задавали в шаблоне в pycharm, то:

1) Удаляем старые конфигурации (все), в них она не подцепится (те которые запускают тесты)

2) Меняем testing tools на pytest <br>
Settings - Tools - Python integrated Tools - Default test runner: pytest

## Не запускаются по порядку тесты (фейлятся после первого прогона): <br>
Запускать со следующими параметрами в config.ini: <br>
DO_NOT_RESTART = True <br>
SOFT_RESTART = False <br>
