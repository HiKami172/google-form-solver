import fire
import pandas as pd
import validators
import re
import yaml

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


def load_config(filepath):
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config


def fetch_html(url, driver_options):
    options = webdriver.ChromeOptions()
    args = driver_options.get('args')
    for arg in args:
        options.add_argument(f"--{arg}")

    driver = webdriver.Chrome(options)
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    driver.close()
    return soup


def is_valid_url(url, patterns):
    patterns = [re.compile(pattern) for pattern in patterns]
    match_pattern = lambda pattern: pattern.match(url)
    return validators.url(url) and any(map(match_pattern, patterns))


def solve(url, answers_file, config="config.yml"):
    ################### Load Config #####################
    cfg = load_config(config)

    url_patterns = cfg.get('url_patterns')
    post_headers = cfg.get('headers')
    driver_options = cfg.get('driver_options')

    #####################################################
    if not is_valid_url(url, url_patterns):
        raise ValueError("Invalid google form url")

    soup = fetch_html(url, driver_options)

    form = soup.find('form')
    entry_tags = form.find_all(
        name='input',
        attrs={
            'type': 'hidden',
            'name': re.compile('^entry\.\d{9,10}$')
        },
    )
    sentinel_tags = form.find_all(
        name='input',
        attrs={
            'type': 'hidden',
            'name': re.compile('^entry\.\d{9,10}_sentinel$')
        },
    )

    entries = [tag['name'] for tag in entry_tags]
    sentinels = [tag['name'] for tag in sentinel_tags]
    for sentinel in sentinels:
        entries.append(sentinel.removesuffix('_sentinel'))

    answers_df = pd.read_csv(answers_file, header=None)
    answers = answers_df.iloc[0].values

    additional_payload = {
        'dlut': 1694128079771,
        'fvv': 1,
        'partialResponse': [None, None, "-2430334359103828238"],
        'pageHistory': 0,
        'fbzx': -2430334359103828238,
    }

    post_url = form['action']
    payload = {entry: answer for entry, answer in zip(entries, answers)}
    for sentinel in sentinels:
        payload[sentinel] = ''

    payload.update(additional_payload)
    session = requests.Session()
    response = session.post(post_url, headers=post_headers, data=payload)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return f"Post error: {e}"

    session.close()


if __name__ == '__main__':
    fire.Fire()
