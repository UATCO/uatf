

### Настройка фреймворка:
1. Скопировать модуль uatf в виртуальное окружение venv/lib/python/site-packages
2. Установить зависимые библиотеки из файла requirements.txt в модуле uatf <br> Для этого открываем модуль в терминале и вбиваем **python -m pip install -r requirements.txt**
3. Перейти в Run -> Edit Configurations -> Edit configurations templates
 -> pytest. <br> 
4. В пункте Environment variables указать **PYTEST_PLUGINS=uatf.pytest_core.fixtures.subtests,uatf.pytest_core.plugin**


#### Разбор частых проблем [тут](FAQ.md).