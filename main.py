import base64
import json
import logging
import os
import time

import requests
from nacl import encoding, public


RUN_TIMES = os.environ['RUN_TIMES']
GITHUB_REPO = os.environ['GITHUB_REPO']
ACTION_TOKEN = os.environ['ACTION_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_URI = os.environ['CLIENT_URI']
CLIENT_TOKEN = os.environ['CLIENT_TOKEN']
CLIENT_SECRET = os.environ['CLIENT_SECRET']


def encrypt(key, value):
    key = public.PublicKey(key.encode('utf-8'), encoding.Base64Encoder())
    box = public.SealedBox(key)
    enc = box.encrypt(value.encode('utf-8'))
    return base64.b64encode(enc).decode('utf-8')


def public_key():
    url = f'https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {ACTION_TOKEN}'
    }
    return requests.get(url, headers=headers).json()


def update_secret(name, value):
    key = public_key()
    value = encrypt(key['key'], value)
    url = f'https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{name}'
    data = {
        'key_id': key['key_id'],
        'encrypted_value': value
    }
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {ACTION_TOKEN}'
    }
    requests.put(url, json=data, headers=headers)


def access_token():
    token = json.loads(CLIENT_TOKEN)
    if token.get('expires_at', 0) > round(time.time()):
        return token['access_token']
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token['refresh_token'],
        'client_id': CLIENT_ID,
        'redirect_uri': CLIENT_URI,
        'client_secret': CLIENT_SECRET
    }
    url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    res = requests.post(url, data).json()
    res['expires_at'] = round(time.time()) + res['expires_in']
    update_secret('CLIENT_TOKEN', json.dumps(res))
    return res['access_token']


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S'
    )
    urls = [
        'https://graph.microsoft.com/v1.0/users',
        'https://graph.microsoft.com/v1.0/me/messages',
        'https://graph.microsoft.com/v1.0/me/mailFolders',
        'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
        'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages/delta',
        'https://graph.microsoft.com/v1.0/me/outlook/masterCategories',
        'https://graph.microsoft.com/v1.0/me/drive',
        'https://graph.microsoft.com/v1.0/me/drive/root',
        'https://graph.microsoft.com/v1.0/me/drive/root/children',
        'https://graph.microsoft.com/v1.0/drive/root',
        'https://graph.microsoft.com/beta/users',
        'https://graph.microsoft.com/beta/me/messages',
        'https://graph.microsoft.com/beta/me/mailFolders',
        'https://graph.microsoft.com/beta/me/mailFolders/inbox/messageRules',
        'https://graph.microsoft.com/beta/me/mailFolders/Inbox/messages/delta',
        'https://graph.microsoft.com/beta/me/outlook/masterCategories',
        'https://graph.microsoft.com/beta/me/drive',
        'https://graph.microsoft.com/beta/me/drive/root',
        'https://graph.microsoft.com/beta/me/drive/root/children',
        'https://graph.microsoft.com/beta/drive/root'
    ]
    headers = {'Authorization': access_token()}
    succeed, failed = 0, 0
    run_times = int(RUN_TIMES or 5)
    for run_time in range(run_times):
        for url in urls:
            try:
                if requests.get(url, headers=headers).status_code == 200:
                    succeed += 1
                    logging.info(f'[SUCCEED] {url}')
                else:
                    failed += 1
                    logging.warning(f'[FAILED] {url}')
                    if failed >= 5:
                        raise Exception('[ERROR] FAILED TOO MANY TIMES')
            except requests.exceptions.ConnectionError:
                failed += 1
                logging.warning(f'[FAILED] {url}')
        if run_time < run_times - 1:
            for second in range(10, 0, -1):
                logging.info(f'[SLEEPING] PLEASE WAIT FOR {second} SECONDS')
                time.sleep(1)
    logging.info(f'[FINISHED] SUCCEED:{succeed} FAILED:{failed}')


if __name__ == '__main__':
    main()
