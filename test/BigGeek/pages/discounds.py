from uatf import *
from uatf.ui import *

class Discounts(Region):

    head = Text(By.CSS_SELECTOR, '.catalog-section__title', 'Заголовок')

    def check_load(self):

        self.head.should_be(Displayed)