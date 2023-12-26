import os.path
import pprint
import logging
from faker import Faker
import allure
import pytest
import requests

faker = Faker()


log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'logs_api.log')

def configure_logger(name, log_file):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

base_logger = configure_logger('base_request_logger', log_file)

class BaseRequest:
    def __init__(self, base_url):
        self.base_url = base_url

    def _request(self, url, request_type, data=None, expected_error=False):
        stop_flag = False
        while not stop_flag:
            if request_type == 'GET':
                response = requests.get(url)
            elif request_type == 'POST':
                response = requests.post(url, data=data)
            elif request_type == 'PUT':
                response = requests.put(url, data=data)
            else:
                response = requests.delete(url)

            if not expected_error and response.status_code == 200:
                stop_flag = True
            elif expected_error:
                stop_flag = True
        pprint.pprint(f'{request_type} example')
        pprint.pprint(response.url)
        pprint.pprint(response.status_code)
        pprint.pprint(response.reason)
        pprint.pprint(response.text)
        pprint.pprint(response.json())
        pprint.pprint('**********')
        return response

    def get(self, endpoint, endpoint_id, expected_error=False):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'GET', expected_error=expected_error)
        return response.json()

    def post(self, endpoint, endpoint_id, body):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'POST', data=body)
        return response.json()['message']

    def put(self, endpoint, endpoint_id, body):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'PUT', data=body)
        return 'Updated'

    def delete(self, endpoint, endpoint_id):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'DELETE')
        return 'Deleted'


BASE_URL = 'http://localhost:3000'
base_request = BaseRequest(BASE_URL)

def GET_REQUEST(essence, id):
    essence_info = base_request.get(f'{essence}', id)
    pprint.pprint(essence_info)
    base_logger.info(essence_info)

urlUsers = 'http://localhost:3000/users'

dataUser = {
    'id': 5,
    'name': faker.name(),
    'age': 10
}
def POST_REQUEST(url, data):
    response = requests.post(url, json=data)
    pprint.pprint(response)
    base_logger.info(response)

dataToUpdUser = {'name': "sana", 'age': 12}

def PUT_REQUEST(essence, id, data):
    essence_id = base_request.put(f'{essence}', id, data)
    pprint.pprint(essence_id)
    base_logger.info(essence_id)


def DELETE_REQUEST(essence, id):
    deleted_essence = base_request.delete(f'{essence}', id)
    pprint.pprint(deleted_essence)
    base_logger.info(deleted_essence)

@allure.feature('Add new user')
@allure.story('пользователь добавился в db.json')
def test_similarName():
    user_info = base_request.get('users', 2)
    assert dataToUpdUser["name"] == user_info["name"]
    pass

@allure.feature('Posts length')
@allure.story('3 постов в posts')
def test_value():
    posts = requests.get('http://localhost:3000/posts')
    assert 3 == len(posts.json())


@allure.feature('Delete user')
@allure.story('удаления пользователя с db.json')
def test_deletedData():

    response = requests.get('http://localhost:3000/users')
    users = response.json()
    user_names = [user["name"] for user in users]
    assert "Amelie" not in user_names


@allure.feature('Get studio name')
@allure.story('получение названия конкретной студии')
@pytest.mark.parametrize('studioID', [1, 2, 3])
def test_getStudio(studioID):
    response = requests.get(f'http://localhost:3000/studio/{studioID}')

    studios = response.json()
    studiosName = studios["name"]

    assert response.status_code == 200

    print(f"Studio #{studioID}: {studiosName}")


@allure.feature('Check 200 status')
@allure.story('Проверка наличия статуса 200 после получения всех пользователей / проверка наличия пользователей с определённым id')
@pytest.mark.parametrize('userID', [1, 2, 3])
def test_checkStatus(userID):
    response = requests.get(f'http://localhost:3000/users/{userID}')
    assert response.status_code == 200


@allure.feature('Check this author')
@allure.story('Проверка на автора ')
def test_similarPosts():
    response = requests.get('http://localhost:3000/posts')
    posts = response.json()
    found = False
    for post in posts:
        if post["author"] == "Lorem":
            found = True
            break
    assert found, "Author 'Lorem' not found in the response"


@allure.feature('Count data < 5')
@allure.story('Проверка на кол-во данных design_course меньше 5')
def test_value():
    response = requests.get('http://localhost:3000/design_course')
    assert len(response.json()) < 5

@allure.feature('Check delete data')
@allure.story('проверка удаления данных')
def test_delete():
    response = requests.delete('http://localhost:3000/design_course')
    assert len(response.json()) == 0

@allure.feature('Having photos')
@allure.story('есть ли фотографии у пользователей')
def test_photoProfile():
    response = requests.get('http://localhost:3000/users')
    users = response.json()
    for user in users:
        assert "profile_photo" not in user, "Profile photo not found in user data"


@allure.feature('Check this course')
@allure.story('Проверка есть ли тот или иной курс')
def test_similarPosts():
    response = requests.get('http://localhost:3000/design_course')
    posts = response.json()
    found = False
    for post in posts:
        if post["title"] == "Motion design":
            found = True
            break
    assert found, "Not found in the response"


@allure.feature('Get info about this user')
@allure.story('Проверка получения данных конкретных пользователей')
@pytest.mark.parametrize('userID', [1, 2, 3])
def test_getStudio(userID):
    response = requests.get(f'http://localhost:3000/users/{userID}')

    users = response.json()

    assert response.status_code == 200

    print(f"Studio #{userID}: {users}")



@allure.feature('having this word')
@allure.story('есть ли слово application в комментариях')
def test_photoProfile():
    response = requests.get('http://localhost:3000/comments')
    comments = response.json()
    com_info = [comm["title"] for comm in comments]
    assert "Application" not in com_info


@allure.feature('Get user Hyun')
@allure.story('есть ли автор Hyun в комментариях')
def test_photoProfile():
    response = requests.get('http://localhost:3000/comments')
    authors = response.json()
    for author in authors:
        assert "Hyun" not in author, "Author not found in user data"

@allure.feature('course count > 0')
@allure.story('Проверка на то, действительно ли кол-во данных design_course больше 0')
def test_userValue():
    response = requests.get('http://localhost:3000/users')
    assert len(response.json()) > 0


@allure.feature('Delete all data in users')
@allure.story('проверка удаления данных в users')
def test_userDelete():
    response = requests.delete('http://localhost:3000/users')
    assert len(response.json()) == 0

@allure.feature('Get info about this course')
@allure.story('Проверка получения данных конкретных пользователей')
@pytest.mark.parametrize('courseID', [1, 2, 3])
def test_getDesignCourseInfo(courseID):
    response = requests.get(f'http://localhost:3000/design_course/{courseID}')

    course = response.json()

    assert response.status_code == 200

    print(f"Studio #{courseID}: {course}")

@allure.feature('Get user Mark')
@allure.story('есть ли пользователь Mark')
def test_checkUserName():
    response = requests.get('http://localhost:3000/users')
    users = response.json()
    for user in users:
        assert "Mark" not in user, "Author not found in user data"
