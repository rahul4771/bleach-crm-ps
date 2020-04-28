import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

debug=True

allowed_hosts=['127.0.0.1','localhost'] 

secret_key='sx$k=8(*ad%t%&l_^%8bst0l62f_$0t3k!r4r7h0l_4)65habj'

databases={

'default': {

    'ENGINE': 'django.db.backends.sqlite3',

    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),

    }

}


static_root='/home/ansab/static/'

media_root= '/home/ansab/media/'