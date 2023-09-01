from ...report.db.db_base import DBBase


class ResultBDUI(DBBase):
    """Модель бд для результатов тестов ui"""

    def setup(self):
        cursor = self.conn.cursor()

        cursor.execute('drop table if exists test_results')
        cursor.execute('CREATE TABLE test_results '
                       '(file_name text, '
                       'suite_name text, '
                       'test_name text, '
                       'status text, '
                       'start_time text, '
                       'stop_time text, '
                       'std_out real, '
                       'img_path text, '
                       'gif_path text, '
                       'description text, '
                       'logs_file_path text, '
                       'UNIQUE (file_name, suite_name, test_name) ON CONFLICT REPLACE)')
        self.conn.commit()

    def save_test_result(self, file_name, suite_name, test_name, status, start_time, stop_time, std_out, img_path,
                         gif_path, description, logs_file_path):
        self.cursor.execute("INSERT INTO test_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (file_name, suite_name, test_name, status, start_time,
                             stop_time, std_out, img_path, gif_path, description, logs_file_path))
        self.conn.commit()
