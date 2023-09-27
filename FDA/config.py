import os
from dotenv import load_dotenv

# loads environment variable from .env file
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
RAZORPAY_ID = os.environ.get('RAZORPAY_ID')
RAZORPAY_SECRET_KEY = os.environ.get('RAZORPAY_SECRET_KEY')
DEBUG = os.environ.get('DEBUG') == 'True'
DB_TYPE = os.environ.get('DB_TYPE', 'postgres')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEBUG_TOOLBAR = os.environ.get('DEBUG_TOOLBAR') == 'True'
REJECT_ORDER_WAITING_TIME = os.environ.get('REJECT_ORDER_WAITING_TIME', '600')
BUFFER_TIME = os.environ.get('BUFFER_TIME', '3600')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT')
DB_HOST = os.environ.get('DB_HOST')
SOCIAL_AUTH_GITHUB_KEY = os.environ.get('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_TWITTER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
