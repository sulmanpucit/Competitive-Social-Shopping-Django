import os
from common_settings import *
import dj_database_url

DATABASES = {'default': dj_database_url.config(default='postgres://rlvwccsmhg:MIeA6Waiu1qShR48nNQx@ec2-107-21-206-166.compute-1.amazonaws.com/rlvwccsmhg')}


os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '')
os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')
os.environ['MEMCACHE_SERVERS'] = "mc2.ec2.memcachier.com:11211"
os.environ['MEMCACHE_USERNAME'] = "237cfc"
os.environ['MEMCACHE_PASSWORD'] = "c8442b7942494c9f54c0"

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': os.environ.get('MEMCACHIER_SERVERS', ''),
        'TIMEOUT': 500,
        'BINARY': True,
        'KEY_PREFIX': 'bidstick',
    },
}

SOCKETIO_SERVER = 'powerful-taiga-2596.herokuapp.com'
