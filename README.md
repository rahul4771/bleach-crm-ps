# Bleach-CRM-PS

This projrct is Bleach Kuwait's Customer Relationship Management Project System. Bleach Kuwait is a premium cleaning company located at Kuwait City, Kuwait.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
*Operating System Ubuntu 18.04 
*Install Python 3.5
    $sudo apt update
    $sudo apt install software-properties-common
    $sudo apt install python3.5
*Install Git(version controll)
    $sudo apt-get install git 
*Text Editor Sublime 
```

### Installing & Running

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```

*Install and Create Virtual Environment
	$pip install virtualenv
	$virtualenv my_name
*Activate virtual Environment 
    $cd to my_name path
    $./bin/activate
*Clone the Project
    $git clone https://gitlab.com/crm-ps/bleach-crm-ps.git    
*Install Requirements
    $pip install -r requirements.txt 
*Copy local_settings to bleach_crm_ps folder
*To Run
    $python3 manage.py makemigrations
    $python3 manage.py migrate
    $python3 manage.py runserver
*Create Super User
	$python3 manage.py createsuperuser 
```

### local_settings.py
Copy local_settings.py to bleach_crm_ps Folder

```
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

debug=True

allowed_hosts=['127.0.0.1','localhost'] 

secret_key='<your_secret_key>'

databases={

'default': {

    'ENGINE': 'django.db.backends.sqlite3',

    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),

    }

}


static_root='/home/django/static/'

media_root= '/home/django/media/'


```


## Deployment

What things you need to deploy the software into sever

```
Give examples
```

## Built With

What are the basic building tools for the project

```
Python 3.5
Django 1.11
sqlite3
```

## Versioning

CRM-PS Version 1.0


## Authors

Owner        :   vinayak.muralidharan@bleach-kw.com
Developers   :   ansab m


## License
Copyright © 2020 Bleach Cleaning Company Kuwait

## Acknowledgments

