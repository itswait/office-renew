import os
import logging
import requests


def get_refresh_token():
    with open('refresh_token.txt', 'r', encoding='utf-8') as f:
        return f.readline().strip()


def set_refresh_token(refresh_token):
    with open('refresh_token.txt', 'w', encoding='utf-8') as f:
        f.write(refresh_token)


def get_access_token():
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': get_refresh_token(),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'redirect_uri': 'https://itswait.github.io/tools/microsoft-api-auth'
    }
    url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    res = requests.post(url, data).json()
    refresh_token = res['refresh_token']
    access_token = res['access_token']
    set_refresh_token(refresh_token)
    return access_token


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
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
        'https://graph.microsoft.com/v1.0/drive/root'
    ]
    urls.extend([
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
    ])
    succeed, failed = 0, 0
    try:
        headers = {
            'Authorization': get_access_token()
        }
        for url in urls:
            if requests.get(url, headers=headers).status_code == 200:
                succeed += 1
                logging.info(f'[SUCCEED] {url}')
            else:
                failed += 1
                logging.warning(f'[FAILED] {url}')
    except Exception as ex:
        logging.exception(ex)
    finally:
        logging.info(f'[FINISHED] SUCCEED:{succeed} FAILED:{failed}')


if __name__ == '__main__':
    main()
