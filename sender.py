import time

import pandas as pd
import requests

url = 'https://docs.google.com/forms/d/e/1FAIpQLSeZvSKxzfUACSiiTXaRNXDuCtAoT0Vrf58ozVxsCi2fulV1Ug/formResponse'
headers = {'User-Agent': 'Mozilla/5.0'}
data = pd.read_excel("answers/Nikee.xlsx", header=0).values


def send_form(answers):
    payload = {
        'entry.1258871590': f'{answers[0].strip()}',
        'entry.1148508615': f'{answers[1].strip()}',
        'entry.1239696069': f'{answers[2].strip()}',
        'entry.279522948': f'{answers[3].strip()}',
        'entry.306482657': f'{answers[4].strip()}',
        'entry.784612407': f'{answers[5].strip()}',
        'entry.967882430': f'{answers[6].strip()}',
        'entry.2113650960': f'{answers[7].strip()}',
        'entry.551199300': f'{answers[8].strip()}',
        'entry.53479424': f'{answers[9].strip()}',
        'entry.809549154': f'{answers[10].strip()}',
        'entry.1362669179': f'{answers[11].strip()}',
        'entry.334329253': f'{answers[12].strip()}',
        'entry.11512501': f'{answers[13].strip()}',
        'entry.1455276698': f'{answers[14].strip()}',
        'entry.1272975677': f'{answers[15].strip()}',
    }

    session = requests.Session()
    response = session.post(url, headers=headers, data=payload)
    print(answers)
    print(response.status_code)
    session.close()


for answers in data:
    send_form(answers)
    time.sleep(1)
