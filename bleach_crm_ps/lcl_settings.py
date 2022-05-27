import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

debug=True

allowed_hosts=['127.0.0.1','localhost','my.bleachkw.com']

secret_key='sx$k=8(*ad%t%&l_^%8bst0l62f_$0t3k!r4r7h0l_4)65habj'

databases = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bleachtest_db',
        'USER': 'bleachtestuser',
        'PASSWORD': 'bleachtestuser',
        'HOST': '',
        'PORT': '',
    }
}

static_root = '/home/static/'
media_root  = '/home/media/'
