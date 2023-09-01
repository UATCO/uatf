# coding=utf-8
import os
import shutil
import string
import json
import sys
import argparse
import glob


def report(results):
    part_4 = ""
    for result in results:
        if result['success']:
            part_ = """<div class="section section_status_success">"""
        else:
            part_ = """<div class="section section_status_fail">"""
        part_ += string.Template("""<div class="section__title">$suite</div>""").substitute(suite=result['suite'])
        part_ += """<div class="section__body section__body_guided">"""
        for case in result['cases']:
            if case['success']:
                part_ += """<div class="section section_status_success">"""
            else:
                part_ += """<div class="section section_status_fail">"""
            part_ += string.Template("""<div class="section__title">$case</div>""").substitute(case=case['case'])
            part_ += """<div class="section__body section__body_guided">"""
            for state in case['states']:
                if state['success']:
                    part_ += """<div class="section section_status_success">"""
                else:
                    part_ += """<div class="section section_status_fail">"""
                part_ += string.Template("""<div class="section__title">$state</div>""") \
                    .substitute(state=state['state'])
                part_ += """<div class="section__body section__body_guided">"""
                for browser in state['browsers']:
                    if browser['success']:
                        part_ += """<div class="section section_status_success">"""
                    else:
                        part_ += """<div class="section section_status_fail">"""
                    part_ += string.Template("""<div class="section__title">$browser</div>""") \
                        .substitute(browser=browser['browser'])
                    part_ += """<div class="section__body">"""
                    if browser['success']:
                        try:
                            part_ += string.Template("""<div class="image-box"><div class="image-box__image">
    <img src="$ref"/></div></div>""").substitute(ref=browser['ref'])
                        except KeyError as e:
                            print('Не смогли сгенерировать данные для HTML отчета\nSuite: %s\nCase: %s\nState: %s'
                                  % (result['suite'], case['case'], state['state']))
                            raise e
                    else:
                        part_ += string.Template("""<div class="image-box"><div class="image-box__image">
    <div class="image-box__title">Expected</div><img src="$ref"/></div><div class="image-box__image">
    <div class="image-box__title">Actual</div><img src="$cur"/></div><div class="image-box__image">
    <div class="image-box__title">Diff</div><img src="$diff"/></div></div>""").substitute(ref=browser['ref'],
                                                                                          cur=browser['cur'],
                                                                                          diff=browser['diff'])
                    part_ += """</div>"""
                    part_ += """</div>"""
                part_ += """</div>"""
                part_ += """</div>"""
            part_ += """</div>"""
            part_ += """</div>"""
        part_ += """</div>"""
        part_ += """</div>"""
        part_4 += part_
    return part_4


def generate_html(report_dir, output=None):
    """Сгенерировать отчет html
    :params report_dir - папка с отчетами
    :params output -  папка куда нужно сохарнить html
    """

    if not os.path.exists(report_dir):
        raise Exception("Папка %s с отчетом не существует" % report_dir)

    # сохраним html в папке с отчетами
    output = output if output else report_dir

    jobs_file = []
    rep = os.path.join(report_dir, "**", "report.json")
    for filename in glob.iglob(rep, recursive=True):
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                jobs_file.append(json.load(json_file))

    if jobs_file:
        total = 1
        failed = 0
        part_1 = """<!DOCTYPE html><html><head><title>ATF regression report</title>
               <link rel="stylesheet" type="text/css" href="report.css"></head><body class="report">
               """
        _b = """<div class="expand"><button id="expandAll" class="button">Expand all</button>
                <button id="collapseAll" class="button">Collapse all</button><button id="expandErrors" 
                class="button">Expand errors</button></div>"""
        part_s = ""
        part_f = ""
        for results in jobs_file:
            total += int(results["total"])
            failed += int(results["failed"])
            part_f += report(results["result"]['failed'])
            part_s += report(results["result"]['success'])

        percent_f = "%s" % (round((failed / total) * 100)) + '%'
        percent_s = "%s" % (100 - round((failed / total) * 100)) + '%'
        part_2 = '<div class="block"> <h1 class="center">Regression Report</h1>' \
                 '<div class="progressbar"> ' \
                 '<div class="bg-danger" style="width: %s"><p>%s</p></div> ' \
                 '<div class="bg-success" style="width: %s"><p>%s</p></div></div>%s</div> <div class="scroll" > ' \
                 % (percent_f, failed, percent_s, (total - failed), _b)
        part_3 = "<h2 class='red'>Failed tests: %s</h2>" % failed
        part_4 = "<h2 class='green'>Success tests: %s</h2>" % (total - failed)
        part_5 = """</div><script src="report.js"></script></body></html>"""

        with open(os.path.join(output, 'report.html'), 'w') as f:
            f.write(part_1)
            f.write(part_2)
            f.write(part_3)
            f.write(part_f)
            f.write(part_4)
            f.write(part_s)
            f.write(part_5)

        path = os.path.dirname(os.path.realpath(__file__))
        shutil.copy(os.path.join(path, 'css', 'report.css'), output)
        shutil.copy(os.path.join(path, 'css', 'report.js'), output)


if __name__ == '__main__':
    ar = argparse.ArgumentParser(add_help=False)
    ar.add_argument("-reports_dir", help="reports folder")
    ar.add_argument("-output_dir", help="output folder")
    options = ar.parse_args(sys.argv[1:])
    options_vars = vars(options)
    report_dir = options_vars['reports_dir']
    output_dir = options_vars.get('output_dir')
    generate_html(report_dir, output_dir)
