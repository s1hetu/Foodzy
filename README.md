
<h1><i> Food Delivery App</i></h1>

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

## Prerequisites 
### Technology 
* Python 3.8.10 
* git version 2.25.1
### Database 
* psql (PostgreSQL) 12.12

### Testing Tools 
* Postman 

### IDE 
* PyCharm

## Postgres Database Setup
```console
CREATE DATABASE dbname;
```
## Configuration in .env file
### Django
```console
SECRET_KEY=66 character long
DB_TYPE=sqlite or postgres. Default is postgres
```
### Database
```console
DB_USER=your username
DB_PASS=your user password
DB_NAME=your database name 
DB_HOST=database host 
DB_PORT=DB Port Number
```

### Email
```console 
EMAIL_HOST_USER= your email_is
EMAIL_HOST_PASSWORD= app password for email
```

### Social Authentication
```console 
SOCIAL_AUTH_GITHUB_KEY= github social auth key
SOCIAL_AUTH_GITHUB_SECRET= github social auth secret
SOCIAL_AUTH_FACEBOOK_KEY= facebook social auth key
SOCIAL_AUTH_FACEBOOK_SECRET= facebook social auth secret
SOCIAL_AUTH_TWITTER_KEY= twitter social auth key
SOCIAL_AUTH_TWITTER_SECRET= twitter social auth secret
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY= google social auth key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET= google social auth secret
```


### Razorpay
```python
pip install razorpay
```
Sign in with google at [razorpay]("https://razorpay.com/") and Navigate to Settings -> API Keys -> Generate API Key


Add those keys as :
```console
RAZORPAY_ID=razorpay ID
RAZORPAY_SECRET_KEY=razorpay secret key
```
<br>

### ngrok
```console
sudo snap install ngrok
```

Sign in with google at [ngrok](https://ngrok.com/) and Navigate to "Your Authtoken"



#### add auth-token for ngrok
```console
ngrok config add-authtoken <YOUR AUTHTOKEN>
```

#### start ngrok service
```console
ngrok http 8000
```
<br>

### Webhook
Sign in with google at [razorpay.com]("https://razorpay.com/") and Navigate to Settings-> Webhooks -> Add new webhook

Copy the url generated from ngrok and Paste the url from ngrok and append "/order/paymenthandler/"

**_Note_** : Your Webhook URL should look like "https://51d9-122-170-103-140.in.ngrok.io/order/paymenthandler/"

Set secret as your RAZORPAY_SECRET_KEY

Set your alert email

Select  "payment.failed" and "payment.captured" from the list of Active Events

Click on Save Webhook


### Extra
```console
BUFFER_TIME=time to expire account activation link in seconds. default is 3600 seconds
REJECT_ORDER_WAITING_TIME=time to wait before auto rejecting placed order. default is 600 seconds
```


## How to clone repository
```console
git clone repo https://gitlab.com/inexture-python/pythonlearning/food_delivery_app_pyverse.git 
```


## Install requirements.txt
```console
pip install -r requirements.txt
```


## Setup Redis
See full installation and commands [here.](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04)
### Install Redis
```console
sudo apt install redis-server
```

### Start Redis
```console
redis-server
```

## Development

### Migrating Databases

When changing models, we have to update the database. Migrations help us track changes.

```console
python manage.py makemigrations
python manage.py migrate
```

### Adding Basic Fixtures
```console
python manage.py loaddata fixtures/groups.json fixtures/state_and_city.json fixtures/categories.json
```

### Adding Testing Fixtures (optional)
```console
python manage.py loaddata fixtures/accounts.json fixtures/delivery_agent.json fixtures/restaurant.json
```
```info 
# Testing Credentials

Admin Users
email: admin@admin.com, password: 123

Customer Users
email: desaiparth971@gmail.com, password: User@0000

Delivery Agent Users
email: ramesh@ramesh.com, password: User@0000
email: agent2@agent.com, password: User@0000
email: agent3@agent.com, password: User@0000

Restaurant Users 
email: owner@owner.com, password: User@0000
email: owner2@owner.com, password: User@0000
```

### Running Server

```console
python manage.py runserver
```

### Running Celery

Worker
```console
celery -A FDA worker --pool=solo -l info
```


Beat
```console
celery -A FDA beat -l info
```
To delete all queued tasks
```console
celery -A FDA purge -Q celery
```


### Testing

To run pytest
```console
pytest
pytest appname appname
```

To run pytest with coverage
```console
coverage run -m pytest
coverage run -m pytest appname appname

```

To See Coverage in console
```console 
coverage report
coverage report -m 
coverage report --source=accounts
coverage report --include=accounts/*
coverage report --omit=*tests/*
```

To See Coverage in html
```console 
coverage html
coverage html --show-contexts
```

To erase collected data in coverage
```console
coverage erase
```

For more information on coverage, read [docs.](https://docs.google.com/document/d/1VKy5pcAuHgOQtu_ITHmLZN_WZleEyDb-IPaYJLb2tpM/edit?usp=sharing)
