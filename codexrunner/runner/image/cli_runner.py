import os
import json
import subprocess

from settings import STAGES


runner_result = {}


def flakehell_processing():
    """Обработка вывода flakehell"""
    flakehell_json_path = 'flakehell.json'
    if os.path.exists(flakehell_json_path):
        with open(flakehell_json_path) as file:
            flakehell_json = json.loads(file.read())

        runner_result['flakehell'].extend([
            'line: {}. {}'.format(item['location']['lines']['begin'], item['description'])
            for item in flakehell_json
        ])


def bandit_processing():
    """Обработка вывода bandit"""
    bandit_json_path = 'bandit.json'
    if os.path.exists(bandit_json_path):
        with open(bandit_json_path) as file:
            bandit_json = json.loads(file.read())

        runner_result['bandit'].extend([
            'line: {}. {}'.format(item['line_number'], item['issue_text'])
            for item in bandit_json['results']
        ])


def pytest_processing():
    """Обработка вывода pytest"""
    pytest_json_path = 'pytest.json'
    if os.path.exists(pytest_json_path):
        with open(pytest_json_path) as file:
            pytest_json = json.loads(file.read())

        if 'tests' in pytest_json:
            runner_result['pytest'].extend([
                item['call']['longrepr']
                for item in pytest_json['tests']
                if item['outcome'] == 'failed'
            ])


if __name__ == '__main__':
    result = {}
    for name, command in STAGES:
        runner_result.setdefault(name, [])
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if name == 'flakehell':
            flakehell_processing()

        if name == 'bandit':
            bandit_processing()

        if name == 'pytest':
            pytest_processing()

    print(json.dumps(runner_result))
