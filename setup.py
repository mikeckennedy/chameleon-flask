import io
import os
import re

from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type('')
    with io.open(filename, mode='r', encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


requires = ['flask[async]', 'Chameleon']

setup(
    name='chameleon_flask',
    version='0.0.1',
    url='https://github.com/mikeckennedy/chameleon-flask',
    license='MIT',
    author='Michael Kennedy',
    author_email='michael@talkpython.fm',
    description='Adds integration of the Chameleon template language to Flask and Quart.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=['chameleon_flask'],
    install_requires=requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)
