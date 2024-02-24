# Social Media API
Social Media API a RESTful API for a social media platform. 
The API allows users to create profiles, follow other users,
create and retrieve posts, manage likes and comments,
and perform basic social media actions.
## Installing using GitHub
Install PostgresSQL and create database

```
git clone https://github.com/IvanMozhar/social_media.git
cd airport_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set DJANGO_SECRET_KEY=<yoursecretkey>
set POSTGRES_HOST=<your db host name>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=<your db password>
python manage.py migrate
python manage.py runserver
```
# Run with Docker
Install and create account in Docker first
```
docker-compose build
docker-compose up
```
### Pull from docker
```
docker pull ivanmozhar/social_media:latest
```

## To get access
- create user via /api/user/register/
- get access token via /api/user/token/

# Project features
- documentation is available by api/doc/swagger/
- adding images to profile: api/social_media/profiles/<int:pk>/upload_image/
- adding images to posts: api/social_media/posts/<int:pk>/upload_image/
- users can only delete likes, add, delete or update comments or profiles if they have created them
- JWT authentication