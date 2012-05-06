DEBUG = False 
#TEMPLATE_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

DATABASES = {
   "default": {
       "ENGINE": "django.db.backends.postgresql_psycopg2", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
       "NAME": "%(db_name)s",                       # Or path to database file if using sqlite3.
       "USER": "%(db_user)s",                             # Not used with sqlite3.
      "PASSWORD": "%(db_passwd)s",                         # Not used with sqlite3.
     "HOST": "%(db_host)s",                             # Set to empty string for localhost. Not used with sqlite3.       "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
   }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '%(memcache)s',
    }
}

CACHE_MIDDLEWARE_SECONDS=60*5
CACHE_MIDDLEWARE_KEY_PREFIX = "foundation-site"



ADMINS = [
     ("Chris Clarke", "cclarke@chrisdev.com"),
]

MANAGERS = [
     ("Chris Clarke", "cclarke@chrisdev.com"),
]


CONTACT_EMAIL='cclarke@chrisdev.com'
