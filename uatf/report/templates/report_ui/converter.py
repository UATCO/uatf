import glob
import os

from bs4 import BeautifulSoup
import codecs


class ConvertReport():

    def __init__(self):
        f = codecs.open("report.html", 'r+', 'utf-8')
        self.report = f.read()

    def get_product(self):
        """Получаем название продукта"""

        product = self.report[self.report.index('<h1>') + 4:self.report.index('</h1>')].split(' ')[-1]
        return product

    def get_test_path(self):
        """Получаем путь до теста"""

        _ = self.report[self.report.index('<a'): self.report.index('>C')].split('\\')
        file_name = _[-1].split(':')[0]
        file_path = f"{self.get_product()}/{_[-4]}/{_[-3]}/{_[-2]}/{file_name}"
        for root, dirs, files in os.walk(file_path):
            print(root)
            print(dirs)
            print(files)
        "/Users/artur_gaazov/UATCO/big_geek_tests/test-auth/smoke/test_auth"
        return file_path

    def convert_link_file(self):
        """Конвертируем ссылку к файлу"""

        old_test_path= self.report[self.report.index('C:'): self.report.index('>C')]
        new_report = self.report.replace(old_test_path, self.get_test_path())



if __name__ == '__main__':
    ConvertReport().convert_link_file()
