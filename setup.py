from setuptools import setup, find_packages


VERSION = '1.9.0.dev0'


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
        'django>=1.8.12,<1.9',
        'django-arcutils>=2.9.1',
        'django-bootstrap-form>=3.2',
        'django-cloak',
        'django-haystack>=2.4.1',
        'django-local-settings>=1.0a20',
        'django-perms>=1.2.1',
        'django-pgcli',
        'djangorestframework>=3.3.3',
        'elasticsearch>=1.9.0,<2.0.0',
        'Markdown>=2.6.6',
        'Pillow>=3.2.0',
        'psycopg2>=2.6.1',
        'pytz>=2016.4',
    ],
    extras_require={
        'dev': [
            'bpython',
            'coverage',
            'flake8',
            'isort',
            'model_mommy',
            'mommy-spatial-generators',
            'psu.oit.arc.tasks',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
