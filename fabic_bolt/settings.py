

from fabric_bolt.core.settings.base import *

CONF_ROOT = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': os.path.join(CONF_ROOT, 'fabric-bolt.db'),
        'USER': 'sqlite3',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SECRET_KEY = '5H6+epoiOP5bndUe0R8vjPFfJEUe4tlwwokFBaTaByHypJm/jfC8lA=='
ALLOWED_HOSTS = ['*']
STATIC_URL = '/static/'
STATIC_ROOT = ''
