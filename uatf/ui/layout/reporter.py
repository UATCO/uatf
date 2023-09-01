import os
import json
from ...config import Config
from ...helper import http_path

config = Config()


def make_report(report_dir, flaky_nodeid: list):

    diff_ext = '~diff'
    cur_ext = '~cur'
    ref_ext = '~ref'
    png_ext = '.png'

    total = 0
    failed = 0
    has_fails = False
    results = []
    results_failed = []
    results_all = {}

    # генерируем отчет
    for suite in os.listdir(report_dir):

        test_dir = os.path.join(report_dir, suite)
        if len(os.listdir(test_dir)) != 0:
            suite_dict = dict(cases=[])
            failed_suite_dict = dict(cases=[])

            for test_name in os.listdir(test_dir):
                case_dict = dict(case=test_name, success=True, states=[])
                state_dir = os.path.join(test_dir, test_name)
                is_failed = False
                for index, state in enumerate(os.listdir(state_dir)):
                    case_dict['states'].append({'state': state, 'success': True})
                    current_state = case_dict['states'][index]
                    current_state['browsers'] = []
                    image_dir = os.path.join(state_dir, state)
                    images = os.listdir(image_dir)
                    browsers = set(map(lambda img: img.replace(png_ext, '')
                                       .replace(ref_ext, '')
                                       .replace(cur_ext, '')
                                       .replace(diff_ext, ''), images))
                    bri = {}
                    for bi, browser in enumerate(browsers):
                        current_state['browsers'].append({'browser': browser, 'success': True})
                        bri[browser] = bi
                        total += 1
                    for image in images:
                        browser = image[:image.find('~')]
                        state_ = image[image.rfind('~') + 1:].replace('.png', '')
                        image_path = os.path.join(image_dir, image)
                        image_path = http_path(image_path)
                        current_state['browsers'][bri[browser]][state_] = image_path
                        if '~diff' in image:
                            # TODO когда появится папка, надо генерировать полный node_id
                            subtest_node = f"{suite}::{case_dict.get('case')}_regression_{os.path.split(image_dir)[-1]}"
                            if subtest_node in flaky_nodeid:  # flaky test
                                flaky_nodeid.remove(subtest_node)
                            else:
                                current_state['browsers'][bri[browser]]['success'] = False
                                current_state['success'] = False
                                case_dict['success'] = False
                                suite_dict['success'] = False
                                failed += 1
                                is_failed = True
                if is_failed:
                    failed_suite_dict['cases'].append(case_dict)
                else:
                    suite_dict['cases'].append(case_dict)

            if len(suite_dict['cases']) != 0:
                results.append({'suite': suite, 'cases': suite_dict['cases'], 'success': True})
            if len(failed_suite_dict['cases']) != 0:
                results_failed.append({'suite': suite, 'cases': failed_suite_dict['cases'], 'success': False})

    if failed > 0:
        has_fails = True

    results.sort(key=lambda i: i['suite'])
    results_all["result"] = {}
    results_all["result"].update({'success': results})
    results_all["result"].update({'failed': results_failed})
    results_all["total"] = total
    results_all["failed"] = failed
    results_all["has_fails"] = has_fails

    if results_all:
        with open(os.path.join(report_dir, 'report.json'), 'w') as f:
            json.dump(results_all, f)
