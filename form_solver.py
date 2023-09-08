import fire
import pandas as pd
import validators
import re
import yaml

import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


def load_config(filepath):
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config


def setup_driver(url, driver_options):
    options = webdriver.ChromeOptions()
    args = driver_options.get('args', [])
    for arg in args:
        options.add_argument(f"--{arg}")

    driver = webdriver.Chrome(options)
    driver.get(url)

    return driver


def is_valid_url(url, patterns):
    patterns = [re.compile(pattern) for pattern in patterns]
    match_pattern = lambda pattern: pattern.match(url)
    return validators.url(url) and any(map(match_pattern, patterns))


def solve(url, answers_file, config="config.yml"):
    ################### Load Config #####################
    cfg = load_config(config)

    url_patterns = cfg.get('url_patterns')
    post_headers = cfg.get('headers')
    driver_options = cfg.get('driver_options', {})

    #####################################################
    if not is_valid_url(url, url_patterns):
        raise ValueError("Invalid google form url")

    driver = setup_driver(url, driver_options)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    form = soup.find('form')

    answers_df = pd.read_csv(answers_file, header=None)
    answers = answers_df.iloc[0].values

    payload = create_payload(form, answers)

    post_url = form['action']

    response = requests.post(post_url, headers=post_headers, data=payload)

    driver.close()

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return f"Post error: {e}"


def create_payload(form, answers):
    payload = {}

    entry_pattern = re.compile('^entry\.\d{9,10}$')
    sentinel_pattern = re.compile('^entry\.\d{9,10}_sentinel$')

    entry_tags = form.find_all('input', attrs={'type': 'hidden', 'name': entry_pattern})
    sentinel_tags = form.find_all('input', attrs={'type': 'hidden', 'name': sentinel_pattern})

    entries = [tag['name'] for tag in entry_tags]

    sentinels = [tag['name'] for tag in sentinel_tags]
    entries.extend([sentinel.removesuffix('_sentinel') for sentinel in sentinels])

    dlut = int(time.time() * 1e3)
    fvv = form.find('input', attrs={'type': 'hidden', 'name': 'fvv'})['value']
    partial_response = form.find('input', attrs={'type': 'hidden', 'name': 'partialResponse'})['value']
    page_history = form.find('input', attrs={'type': 'hidden', 'name': 'pageHistory'})['value']
    fbzx = form.find('input', attrs={'type': 'hidden', 'name': 'fbzx'})['value']

    core_values = {
        'dlut': dlut,  # unix timestamp
        'fvv': fvv,  # google form version
        'partialResponse': partial_response,  # form completion flag
        'pageHistory': page_history,  # user's path through form
        'fbzx': fbzx  # security session id
    }

    payload.update({entry: answer for entry, answer in zip(entries, answers)})
    payload.update({sentinel: '' for sentinel in sentinels})
    payload.update(core_values)
    return payload


if __name__ == '__main__':
    fire.Fire()
