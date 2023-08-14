from uatf import *
from uatf.ui import *


class OrderPage(Region):
    """Страница оформления заказа"""

    login = Button(By.CLASS_NAME, 'login-modal-singin', 'Войти')
    name = TextField(By.CSS_SELECTOR, '[name="name"]', 'Имя')
    surname = TextField(By.CSS_SELECTOR, '[name="last_name"]', 'Фамилия')
    email = TextField(By.CSS_SELECTOR, '[name="email"]', 'Электронная почта')
    phone = TextField(By.CSS_SELECTOR, '[name="phone"]', 'Мобильный телефон')
    comment = TextField(By.CSS_SELECTOR, '[name="comment"]', 'Комментарий к заказу')

    # способы получения заказа
    pickup = Button(FindBy.JQUERY, '.order-form__tab:eq(0)', 'Самовывоз')
    delivery = Button(FindBy.JQUERY, '.order-form__tab:eq(1)', 'Доставка')

    continue_btn = Button(By.CLASS_NAME, 'order-form__proceed', 'Продолжить')
    confirm_order = Button(By.CLASS_NAME, 'step-sticky__submit', 'Подтвердить заказ')

    # детали доставки
    country = Button(By.CLASS_NAME, 'order-form__country-wrap', 'Страна')
    city = Button(By.CLASS_NAME, 'order-form__city-wrap', 'Город')
    street = TextField(By.CSS_SELECTOR, '[id="street"]', 'Улица')
    home_number = TextField(By.CSS_SELECTOR, '[id="house-number"]', 'Номер дома')
    apartament_number = TextField(By.CSS_SELECTOR, '[id="apartament-number"]', '№ кв или офиса')
    additional = TextField(By.CSS_SELECTOR, '[name="additional"]', 'Дополнительно')

    def check_load(self):
        """Првоеряем загрзку страницы"""

        self.name.should_be(Displayed)

    def auth(self, email: str, password: str):
        """Авторизуемся из заказа
        :param email: логин
        :param password: пароль"""

        from pages.auth_panel import AuthPanel
        self.login.click()
        auth_panel = AuthPanel(self.driver)
        auth_panel.check_open()
        auth_panel.auth(email, password)

    def fill_order(self, **kwargs):
        """
        Заполняем поля в заказе
        Имя=''
        Фамилия=''
        Почта=''
        Телефон=''
        Комментарий=''
        """

        for key in kwargs:
            if 'Имя' == key:
                self.name.type_in(kwargs.get('Имя'))
            elif 'Фамилия' == key:
                self.surname.type_in(kwargs.get('Фамилия'))
            elif 'Почта' == key:
                self.email.type_in(kwargs.get('Почта'))
            elif 'Телефон' == key:
                self.phone.type_in(kwargs.get('Телефон'))
            elif 'Комментарий' == key:
                self.comment.type_in(kwargs.get('Комментарий'))

    def fill_ways_to_get(self, pickup: bool = True):
        """Выбираем способ получения
        :param pickup: Самовывоз - True, Доставка - False
        """

        if pickup:
            self.pickup.click()
        else:
            self.delivery.click()

    def next_step(self):
        """Переходим к следующему шагу"""

        self.continue_btn.click()

    def confirm(self):
        """Подверждаем заказ"""

        self.confirm_order.click()

    def fill_delivery_data(self, **kwargs):
        """Заполняем данные по доставке
        Страна=''
        Город=''
        Улица=''
        НомерДома=''
        НомерКв=''
        Дополнительно=''
        """

        for key in kwargs:
            if 'Страна' == key:
                self.country.element(By.CLASS_NAME, 'order-form__country-label-country').click()
                self.country.element(By.CLASS_NAME, 'order-form__country-input', element_type=TextField).type_in(
                    kwargs.get('Страна'))
                self.country.element(By.CLASS_NAME, 'order-form__country-item', element_type=CustomList).item(
                    contains_text=kwargs.get('Страна')).click()
            elif 'Город' == key:
                self.city.element(By.CLASS_NAME, 'order-form__city-label-city').click()
                self.city.element(By.CLASS_NAME, 'order-form__city-input', element_type=TextField).type_in(
                    kwargs.get('Город'))
                self.city.element(By.CLASS_NAME, 'order-form__city-item', element_type=CustomList).item(
                    contains_text=kwargs.get('Город')).click()
            elif 'Улица' == key:
                self.street.type_in(kwargs.get('Улица'))
            elif 'НомерДома' == key:
                self.home_number.type_in(kwargs.get('НомерДома'))
            elif 'НомерКв' == key:
                self.apartament_number.type_in(kwargs.get('НомерКв'))
            elif 'Дополнительно' == key:
                self.additional.type_in(kwargs.get('Дополнительно'))
