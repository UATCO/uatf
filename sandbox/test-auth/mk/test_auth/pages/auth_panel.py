from uatf import *
from uatf.ui import *
from selenium.webdriver.common.keys import Keys


class AuthPanel(Region):
    """Панелька авторизации"""

    caption = Text(By.CLASS_NAME, 'login-modal__title', 'Заголовок')
    login = TextField(By.CSS_SELECTOR, '.login-modal__wrap [name="email"]', 'Электронная почта')
    password = TextField(By.CSS_SELECTOR, '[name="current-password"]', 'Пароль')
    auth_btn = Button(By.CLASS_NAME, 'login-modal__login-submit', 'Войти')
    modes = CustomList(By.CLASS_NAME, 'login-modal__item', 'Соцсети для авторизации')

    #форма авторизации гугл
    auth_panel_google = Element(By.CSS_SELECTOR, '[role="presentation"]', 'Панель авторизации гугл')
    login_google = TextField(By.CSS_SELECTOR, '[autocomplete="username"]', 'Электронная почта')
    password_google = TextField(By.CSS_SELECTOR, '[autocomplete="current-password"]', 'Пароль')
    adverb_btn = Button(By.CLASS_NAME, 'VfPpkd-RLmnJb', 'Далее')

    #форма авторизации яндекс
    other_btn = Button(By.CLASS_NAME, 'UserEntryFlow__sign-in-with-yandex-btn', 'Другие способы входа')
    auth_panel_yandex = Element(By.CLASS_NAME, 'passp-auth-content', 'Панель авторизации гугл')
    login_yandex = TextField(By.CSS_SELECTOR, '[name="login"]', 'Электронная почта')
    password_yandex = TextField(By.CSS_SELECTOR, '[name="passwd"]', 'Пароль')
    submit_btn = Button(By.CSS_SELECTOR, '[type="submit"]', 'Войти как')

    def check_open(self):
        """Проверяем открытие панели"""

        self.caption.should_be(Displayed)

    def auth(self, email: str, password: str):
        """Авторизуемся
        :param email: логин
        :param password: пароль"""

        log(f'Вводим логин: {email}')
        self.login.should_be(Displayed)
        self.login.type_in(email)

        log(f'Вводим пароль: {password}')
        self.password.type_in(password)

        self.auth_btn.click()

    def auth_google(self, email: str, password: str):
        """Авторизуемся в гугл
        :param email: логин
        :param password: пароль"""

        auth_site = 'https://accounts.google.com'

        assert_that(lambda : self.browser.site, equal_to(auth_site),
                    desc='Страница авторизации Google не открыта', wait_time=and_wait(5))

        log(f'Вводим логин: {email}')
        self.login_google.should_be(Displayed)
        self.auth_panel_google.check_change(lambda: self.login_google.type_in(f'{email} {Keys.ENTER}'))

        log(f'Вводим пароль: {password}')
        self.password_google.type_in(f'{password} {Keys.ENTER}')

        assert_that(lambda: self.browser.site, not_equal(auth_site),
                    desc='Страница авторизации Google не закрылась', wait_time=and_wait(5))

    def auth_yandex(self, email: str, password: str):
        """Авторизуемся в яндекс
        :param email: логин
        :param password: пароль"""

        auth_site = 'https://passport.yandex.ru'

        assert_that(lambda: self.browser.site, equal_to(auth_site),
                    desc='Страница авторизации Google не открыта', wait_time=and_wait(5))

        self.auth_panel_yandex.check_change(lambda : self.other_btn.click())

        log(f'Вводим логин: {email}')
        self.login_yandex.should_be(Displayed)
        self.auth_panel_yandex.check_change(lambda: self.login_yandex.type_in(f'{email} {Keys.ENTER}'))

        log(f'Вводим пароль: {password}')
        self.password_yandex.type_in(f'{password} {Keys.ENTER}')
        self.submit_btn.click()

        assert_that(lambda: self.browser.site, not_equal(auth_site),
                    desc='Страница авторизации Google не закрылась', wait_time=and_wait(5))


