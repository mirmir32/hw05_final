# yatube
### Описание:
Блог-социальная сеть

Проект позволяет просматривать посты пользователей сайта. Зарегистрированные пользователи могут также оставлять собственные посты и подписываться на других авторов

### Технологии:
```
Python, Django, SQLite, HTML
```
### Как установить проект:

Клонировать репозиторий проекта локально:
```
git clone https://github.com/SergeSGH/hw05_final.git
```
Установить виртуальное коружение, сделать миграции, создать суперпользователя, запустить сайт:
```
python -m venv venv
. venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```