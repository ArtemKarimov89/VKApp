from pprint import pprint

import requests
import json


def get_photos(photos_list, count):
    all_photos = photos_list['response']['items']

    photos_name_list = []

    likes_list = []

    for item in all_photos:
        if len(photos_name_list) == max_photos:
            break

        photo_params = {}
        likes = item['likes']['count']
        if likes in likes_list:
            file_name = f'{likes}_{item['date']}.jpg'
        else:
            file_name = f'{likes}.jpg'

        size_params = item['sizes'][-1]

        photo_params['file_name'] = file_name
        photo_params['size'] = size_params['type']
        photo_params['url'] = size_params['url']

        photos_name_list.append(photo_params)
        likes_list.append(likes)

    return photos_name_list


def create_log_file(data):
    with open('log.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=2))


class VK:
    BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token, user_id, version='5.199'):
        self.token = access_token
        self.id = f'id{user_id}'
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_photos(self, owner_id, album_id):
        params = {'user_ids': self.id, 'owner_id': owner_id, 'album_id': album_id, 'extended': 1}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}photos.get', params=params)
        return response.json()


class YD:
    BASE_URL = 'https://cloud-api.yandex.net'

    def __init__(self, y_token):
        self.token = y_token
        self.headers = {'Authorization': f'OAuth {y_token}'}

    def create_dir(self, dir_name):
        params = {'path': f'{dir_name}'}
        response = requests.put(f'{self.BASE_URL}/v1/disk/resources', params=params, headers=self.headers)

    def photos_backup(self, photos_list, folder_name):
        if folder_name == "":
            folder_name = 'profile_photos'
        self.create_dir(folder_name)

        for photo in photos_list:
            params = {'path': f'{folder_name}/{photo['file_name']}',
                      'overwrite': True,
                      'url': photo.pop('url')}
            response = requests.post(f'{self.BASE_URL}/v1/disk/resources/upload',
                                     params=params,
                                     headers=self.headers)
        create_log_file(photos_list)


if __name__ == '__main__':
    print('Пожалуйста, введите сервисный ключ')
    access_token = input()  # сервисный ключ
    print('Пожалуйста, введите токен с полигона Yandex')
    y_token = input()  # токен с полигона Yandex
    print('Пожалуйста, введите идентификатор пользователя VK')
    user_id = int(input())  # идентификатор пользователя VK
    print('Пожалуйста, введите имя папки, куда будет сохранены фотографии профиля')
    folder_name = input()

    vk = VK(access_token, user_id)
    all_photos = vk.get_photos(user_id, 'profile')

    max_photos = 5
    photos_list = get_photos(all_photos, max_photos)

    y_disk = YD(y_token)
    y_disk.photos_backup(photos_list, folder_name)
    print('Логи находятся в файле "log.json"')
