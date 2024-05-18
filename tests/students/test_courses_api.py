from model_bakery import baker
from rest_framework.test import APIClient
import pytest

from students.models import Student, Course


# Фикстура для APIClient
@pytest.fixture
def client():
    return APIClient()


# Фикстура для фабрики студентов
@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


# Фикстура для фабрики курсов
@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


# Тест получения 1 курса
@pytest.mark.django_db
def test_get_course_1(client, course_factory):
    # Через фабрику создаем 1 курс
    course = course_factory(_quantity=1)
    # Делаем запрос по урлу, сохраняем в переменную response
    response = client.get('/api/v1/courses/')
    # Проверяем код ответа
    assert response.status_code == 200
    # Преобразуем полученные данные response в словарь json
    data = response.json()
    # Проверяем, что кол-во элементов словаря = кол-ву элементов фабрики
    assert len(data) == len(course)
    # Сравниваем name из запроса с name из фабрики
    assert data[0]['name'] == course[0].name


# Тест получения списка из 10 курсов. Через фабрику создаем 10 курсов, делаем запрос по урлу,
# Через цикл сравниваем name из запроса с name из фабрики
@pytest.mark.django_db
def test_get_course_list(client, course_factory):
    course = course_factory(_quantity=10)

    response = client.get('/api/v1/courses/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(course)
    for i, m in enumerate(data):
        assert m['name'] == course[i].name


# Тест фильтрации списка курсов по id и name
@pytest.mark.django_db
def test_get_course_filter(client, course_factory):
    course = course_factory(_quantity=10)

    response = client.get('/api/v1/courses/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(course)
    # Через цикл сравниваем id и name из запроса с id и name из фабрики
    for i, m in enumerate(data):
        assert m["id"] == Course.objects.values()[i]["id"]
        assert m["name"] == Course.objects.values()[i]["name"]
        assert m["id"] == course[i].id
        assert m["name"] == course[i].name


# Альтернативный тест фильтрации списка курсов по id и name
@pytest.mark.django_db
def test_get_course_filter_2(client, course_factory):
    course = course_factory(_quantity=10)
    # Получаем из запроса запись, id и name которой соответствуют записи №5 из фабрики
    response = client.get(f'/api/v1/courses/?id={course[5].id}&name={course[5].name}')

    assert response.status_code == 200
    data = response.json()
    # Сравниваем id и name записи из запроса с id и name записи №5 из фабрики
    assert data[0]['id'] == course[5].id
    assert data[0]['name'] == course[5].name


# Тест успешного создания курса
@pytest.mark.django_db
def test_create_course(client, course_factory):
    # Получаем кол-во курсов в таблице
    count = Course.objects.count()
    data = {'name': 'text name'}
    # Создаем в таблице курс у которого name - text name
    response = client.post('/api/v1/courses/', data)
    data_response = response.json()
    assert response.status_code == 201
    # Сравниваем значение name из словаря data со значением name, записанным в таблицу
    assert data['name'] == data_response['name']
    # Проверяем, что в таблицу добавилась 1 запись
    assert Course.objects.count() == count + 1


# Тест успешного обновления курса
@pytest.mark.django_db
def test_update_course(client, course_factory):
    # Через фабрику создаем 1 курс
    course = course_factory(_quantity=1)
    data = {'name': 'text name'}
    # Обновляем запись в поле name значением 'text name'
    response = client.patch(f'/api/v1/courses/{course[0].id}/', data)
    assert response.status_code == 200
    data_response = response.json()
    # Сравниваем значение name из словаря data со значением name, записанным в таблицу
    assert data_response['name'] == data['name']
    assert Course.objects.get(id=course[0].id).name == data['name']


# Тест успешного удаления курса
@pytest.mark.django_db
def test_delete_course(client, course_factory):
    # Получаем кол-во курсов в таблице
    count = Course.objects.count()
    # Через фабрику создаем 1 курс
    course = course_factory(_quantity=1)
    # Удаляем из таблицы запись по заданному id (которая записана через фабрику)
    response = client.delete(f'/api/v1/courses/{course[0].id}/')
    assert response.status_code == 204
    # Проверяем, что в таблице после записи и удаления исходное кол-во записей
    assert Course.objects.count() == count
    # Проверяем, что id созданной через фабрики записи отсутствует в списке id таблицы Course
    assert course[0].id not in [i.id for i in Course.objects.all()]