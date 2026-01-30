docker-compose down
docker-compose up -d --build

docker exec fnb_ho_web python manage.py create_test_user
