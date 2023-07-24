import string

with open("/Users/artur_gaazov/Documents/uatf/uatf/report/template_ui.html") as tpl:
    template = string.Template(tpl.read())


class ReportUI:
    """Класс для создания отчета"""

    def __init__(self, file_name: str, suite_name: str, test_name: str, status: str, std_out: str, start_time: str,
                 stop_time: str, template=template):
        self.file_name = file_name
        self.suite_name = suite_name
        self.test_name = test_name
        self.status = status
        self.std_out = std_out
        self.start_time = start_time
        self.stop_time = stop_time

        final_output = template.safe_substitute(file_name=self.file_name, suite_name=self.suite_name,
                                                test_name=self.test_name, status=self.status,
                                                start_time=self.start_time, stop_time=self.stop_time,
                                                std_out=self.std_out)
        with open("report.html", "a") as output:
            output.write(final_output)
