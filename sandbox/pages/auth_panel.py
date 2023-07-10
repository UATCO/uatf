from uatf import *
from uatf.ui import *


class AuthPanel(Region):
    """Панелька авторизации"""

    caption = Text(By.CLASS_NAME, 'login-modal__title', 'Заголовок')
    login = TextField(By.CSS_SELECTOR, '[name="email"]', 'Электронная почта')
    password = TextField(By.CSS_SELECTOR, '[name="current-password"]', 'Пароль')
    auth_btn = Button(By.CLASS_NAME, 'login-modal__login-submit', 'Войти')

    def check_open(self):
        """Проверяем открытие панели"""

        self.caption.should_be(Displayed)

    def auth(self, email: str, password: str):
        """Авторизуемся
        :param email: логин
        :param password: пароль"""

        log(f'Вводим логин: {email}')
        self.login.type_in(email)

        log(f'Вводим пароль: {password}')
        self.password.type_in(password)

        self.auth_btn.click()


