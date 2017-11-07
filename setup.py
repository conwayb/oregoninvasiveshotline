from setuptools import setup, find_packages


VERSION = '1.12.0.dev0'


setup(
    name='psu.oit.arc.oregoninvasiveshotline',
    version=VERSION,
    description='Oregon Invasives Hotline',
    author='PSU - OIT - ARC',
    author_email='consultants@pdx.edu',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'psu.oit.wdt.emcee>=1.0.0.dev0',
        'django>=1.8.18,<1.9',
        'django-arcutils>=2.24.0',
        'django-bootstrap-form>=3.2.1',
        'django-cloak',
        'django-haystack>=2.4.1,<2.5',
        'django-perms>=2.0.0',
        'django-pgcli>=0.0.2',
        'djangorestframework>=3.6.4,<3.7',
        'elasticsearch>=1.9.0,<2.0.0',
        'Markdown>=2.6.8',
        'Pillow>=4.3.0',
        'psycopg2>=2.7.3.1',
        'pytz>=2017.2',
    ],
    extras_require={
        'dev': [
            'bpython',
            'coverage',
            'flake8',
            'model_mommy',
            'docker-compose'
        ]
    },
)
