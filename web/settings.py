DEBUG = True

SECRET_KEY = 'put_your_key_here'

#
# CELERY CONFIG 
#
# in the url don't forget to change the password both here and in 
# the docker-compose cmd
CELERY_BROKER_URL = 'redis://:password@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:password@redis:6379/0'
