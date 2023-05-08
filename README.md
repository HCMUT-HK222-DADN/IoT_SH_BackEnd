# BackEnd

```
    env\Scripts\activate.bat
    pip install -r path\requirement.txt
```

# Tạo app

```
    python manage.py startapp {app_name}
```

# Mapping các thực thể ERD sang models.py

    Note: 
        + Trước khi chạy python manage.py migrate phải tạo database trên MySQL Workbench
        + Tạo một số dữ liệu mẫu để test APIs
```
    python manage.py makemigrations {app_name}?
    python manage.py migrate
```

# Run Server

```
    python manage.py runserver
```

# Run Websocket
```
daphne -b {your_ip} iot_backend.asgi:application
```