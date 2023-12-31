from ..config import Config
from selenium.webdriver import ActionChains
from ..logfactory import log
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction


class ActionChainsUATF(object):
    """Класс для реализации различных взаимодействий, таких как клик, пермещение, нажатие клавиш"""

    def __init__(self, driver):

        self.driver = driver
        self.config = Config()
        self.chain = ActionChains(self.driver)
        self.__logs = []
        if self.config.GENERAL.get("CHROME_MOBILE_EMULATION"):
            self.chain.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))

    def reset_action(self):
        """Clear all stored actions."""

        self.chain.reset_actions()

    def perform(self):
        """
        Performs all stored actions.
        """
        logs = self.__logs

        self.chain.perform()

        log('Выполняем цепочку действий:\n  * ' + '\n  * '.join(logs), "[a]")
        self.__logs = []

    def click(self, on_element=None):
        """ Клик по элементу
            :param on_element элемент, по которому кликаем
            Если None, кликаем в текущее положение курсора
        """

        if on_element:
            name_element = on_element.name_output()
            on_element = on_element.webelement()
            self.__logs.append("Навели мышку над {0}".format(name_element))
        else:
            name_element = "текущему элементу"

            self.chain.click(on_element)

        self.__logs.append("Кликнули по {0}".format(name_element))
        return self

    def click_and_hold(self, on_element=None):
        """ Зажать курсор мыши над элементом
            :param on_element элемент, над которым зажимаем курсор мыши
            Если None, то зажать в текущем положении
        """

        if on_element:
            name_element = on_element.name_output()
            on_element = on_element.webelement()
            self.__logs.append("Навели мышку над {0}".format(name_element))
        else:
            name_element = "текущим элементом"

        self.chain.click_and_hold(on_element)
        self.__logs.append("Зажали курсор мыши над {0}".format(name_element))

        return self

    def pause(self, seconds=0.05):
        """ Задержка между действиями
            :param seconds задержка
        """

        self.chain.pause(seconds)
        self.__logs.append(f"Задержка между действиями на {seconds}")
        return self

    def context_click(self, on_element=None):
        """ Клик правой кнопкой мыши по элементу
            :param on_element элемент, по которому кликаем
            Если None, кликаем в текущее положение курсора
        """

        if on_element:
            name_element = on_element.name_output()
            on_element = on_element.webelement()
            self.__logs.append("Навели мышку над {0}".format(name_element))
        else:
            name_element = "текущему элементу"

        self.chain.context_click(on_element)
        self.__logs.append("Кликнули правой кнопкой мыши по {0}".format(name_element))

        return self

    def middle_button_click(self, on_element=None):
        """ Клик средней кнопкой мыши по элементу
            :param on_element элемент, по которому кликаем
            Если None, кликаем в текущее положение курсора
        """

        if on_element:
            name_element = on_element.name_output()
            self.move_to_element(on_element)
            self.__logs.append(f"Навели мышку над {name_element}")
        else:
            name_element = "текущему элементу"

        self.chain.w3c_actions.pointer_action.pointer_down(1)
        self.chain.w3c_actions.pointer_action.pointer_up(1)
        self.chain.w3c_actions.key_action.pause()
        self.chain.w3c_actions.key_action.pause()
        self.__logs.append(f"Кликнули средней кнопкой мыши по {name_element}")

        return self

    def move_to_element(self, to_element):
        """ Переместить курсор мыши на середину элемента
            :param to_element элемент, на который перемещаем курсор мыши
        """

        self.chain.move_to_element(to_element.webelement())
        self.__logs.append("Навели мыши на середину элемента {0}".format(to_element.name_output()))

        return self

    def double_click(self, on_element=None):
        """ Двойной клик по элементу
            :param on_element элемент, по которому кликаем
            Если None, кликаем в текущее положение курсора
        """

        if on_element:
            name_element = on_element.name_output()
            on_element = on_element.webelement()
            self.__logs.append("Навели мышку над {0}".format(name_element))
        else:
            name_element = "текущему элементу"

        self.chain.double_click(on_element)
        self.__logs.append("Выполнили двойной клик по {0}".format(name_element))

        return self

    def drag_and_drop(self, source, target):
        """ Перемещение элемента source на элемент target
            :param source элемент, который перемещаем
            :param target элемент, на который перемещаем
        """

        self.click_and_hold(source)
        self.move_to_element(target)
        self.release(target)

        return self

    def release(self, on_element=None):
        """ Отпустить курсор мыши над элементом
            :param on_element элемент, над которым отпустить курсор мыши
            Если None, то отпустить в текущем положении
        """

        if on_element:
            name_element = on_element.name_output()
            on_element = on_element.webelement()
            self.__logs.append("Навели мышку над {0}".format(name_element))
        else:
            name_element = "текущим элементом"

        self.chain.release(on_element)
        self.__logs.append("Отпустили курсор мыши над {0}".format(name_element))

        return self

    def send_keys(self, *keys_to_send):
        """ Посылаем текущему элементу набор кнопок на клавиатуре
        :param: keys_to_send набор кнопок (Описание находится в классе 'Keys')
        """

        self.chain.send_keys(*keys_to_send)
        self.__logs.append("Зажали набор кнопок над текущим элементом")
        return self

    def send_keys_to_element(self, element, *keys_to_send):
        """ Посылаем указанному элементу набор кнопок на клавиатуре
        Sends keys to an element.
        :param element элемент
        :param keys_to_send набор кнопок (Описание находится в классе 'Keys')
        """

        self.chain.send_keys_to_element(element.webelement(), *keys_to_send)
        self.__logs.append("Зажали кнопки над {0} ".format(element.name_output()))
        return self

    def swipe(self, element):
        """Сделать свайп по указанному элементу
        :param element элемент
        """

        rect = element.rect

        start_point_x = rect["x"] + rect["width"] / 2
        start_point_y = rect["y"] + rect["height"] / 2

        end_point_x = start_point_x / 2
        end_point_y = start_point_y

        self.chain.w3c_actions.pointer_action.move_to_location(start_point_x, start_point_y).pointer_down()
        self.chain.w3c_actions.pointer_action.pause(0.5)
        self.chain.w3c_actions.pointer_action.move_to_location(end_point_x, end_point_y).release()
        self.__logs.append("Сделали свайп по элементу {0}".format(element.name_output()))
        return self

    def key_down(self, value, element=None):
        """ Зажать кнопку клавиатуры над элементом или над элементом в фокусе.
            (Использовать клавиши Control, Alt and Shift)

        :param value - кнопка
        :param element элемент, над которым зажимаем клавишу
            Если None, зажимаем над элементом в фокусе

        Пример, комбинации клавиш ctrl+c:

            ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()

        """

        if element:
            name_element = element.name_output()
            element = element.webelement()
            self.__logs.append("Кликнула по элементу {0}".format(name_element))
        else:
            name_element = "текущим элементом"

        self.chain.key_down(value, element)
        self.__logs.append("Зажали клавишу над {0}".format(name_element))

        return self

    def move_to_element_with_offset(self, to_element, xoffset, yoffset):
        """ Переместить курсор мыши на смещение относительно центра элемента

            :param to_element элемент, отномительно которого смещаем
            :param xoffset смещение по оси X
            :param yoffset смещение по оси Y
        """

        self.chain.move_to_element_with_offset(to_element.webelement(), xoffset, yoffset)
        self.__logs.append("Переместили мышь относительно центра элемента {0} на смещение ({1}, {2})"
                           .format(to_element.name_output(), xoffset, yoffset))
        return self

    def move_to_element_corner_with_offset(self, to_element, xoffset, yoffset):
        """ Переместить курсор мыши на смещение относительно левого верхнего угла элемента
        * для перехода на selenium 4

            :param to_element элемент, отномительно которого смещаем
            :param xoffset смещение по оси X
            :param yoffset смещение по оси Y
        """
        el_rect = to_element.rect
        left_offset = el_rect['width'] / 2
        top_offset = el_rect['height'] / 2
        left = -left_offset + (xoffset or 0)
        top = -top_offset + (yoffset or 0)
        self.chain.move_to_element_with_offset(to_element.webelement(), xoffset=int(left), yoffset=int(top))
        self.__logs.append("Переместили мышь относительно верхнего левого угла элемента {0} на смещение ({1}, {2})"
                           .format(to_element.name_output(), xoffset, yoffset))
        return self

    def key_up(self, value, element=None):
        """ Отпустить кнопку клавиатуры над элементом или над элементом в фокусе
            (Использовать клавиши Control, Alt and Shift)

        :param value - кнопка
        :param element элемент, над которым отпускаем клавишу
            Если None, отпускаем над элементом в фокусе

        Пример, комбинации клавиш ctrl+c:

            ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()

        """

        if element:
            name_element = element.name_output()
            element = element.webelement()
            self.__logs.append("Кликнула по элементу {0}".format(name_element))
        else:
            name_element = "текущим элементом"

        self.chain.key_up(value, element)
        self.__logs.append("Отпустили клавишу над {0}".format(name_element))
        return self

    def move_by_offset(self, xoffset, yoffset):
        """ Переместить курсор мыши на заданное смещение
            :param xoffset смещение по оси X
            :param yoffset смещение по оси Y
        """

        self.chain.move_by_offset(xoffset, yoffset)
        self.__logs.append("Переместили курсор мыши на смещение ({0}, {1})".format(xoffset, yoffset))

        return self
