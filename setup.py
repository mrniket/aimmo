# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

import versioneer

setup(
    name='aimmo',
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django >= 1.8.3, <= 1.9.13',
        'django-autoconfig >= 0.3.6, < 1.0.0',
        'django-forms-bootstrap',
        'django-js-reverse',
        'eventlet',
        'flask',
        'flask-socketio',
        'requests',
        'six',
        'hypothesis',
        'flask-cors >= 3.0, < 3.1',
        'psutil >= 5.4, < 5.5',
    ],
    tests_require=[
        'httmock',
        'mock == 2.0.0',
        'docker == 2.7.0',
        'kubernetes == 5.0.0',
        'PyYAML == 3.12',
    ],

    version=versioneer.get_version(),
    zip_safe=False,
)
