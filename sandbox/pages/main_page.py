from uatf import *
from uatf.ui import *


class MainPage(Region):
    """Главная страница"""

    basket = Button(By.CLASS_NAME, 'header-middle__link', 'Корзина')
    auth_btn = Button(By.CLASS_NAME, 'login-modal-singin', 'Войти')
    account_btn = Button(By.CLASS_NAME, 'user-header-middle__link--account', 'Личный кабинет')

    def open(self):
        """Открываем главную страницу"""

        self.browser.open(self.config.get('SITE', 'GENERAL'))
        self.check_load()

    def check_load(self):
        """Проверка загрузки страницы"""

        self.basket.should_be(Displayed)

    def open_basket(self):
        """Открываем корзину"""

        from sandbox.pages.basket_page import BasketPage

        self.basket.click()
        basket_page = BasketPage(self.driver)
        basket_page.check_load()
        return basket_page

    def open_auth_panel(self):
        """Открываем панель авторизации"""

        from sandbox.pages.auth_panel import AuthPanel

        log('Открываем панель авторизации')
        self.auth_btn.click()
        auth_panel = AuthPanel(self.driver)
        auth_panel.check_open()
        return auth_panel

    def auth(self, email: str, password: str):
        """Авторизуемся
        :param email: логин
        :param password: пароль"""

        auth_pane = self.open_auth_panel()

        log('Авторизуемся')
        auth_pane.auth(email, password)
        self.auth_btn.should_not_be(Displayed)
        self.account_btn.should_be(Displayed)