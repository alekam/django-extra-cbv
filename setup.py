import os.path
from setuptools import setup, find_packages


version = __import__('extra_cbv').get_version()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_requires_list(filename):
    s = open(filename).read().split("\n")
    dependenses = []
    if len(s):
        for pkg in s:
            if pkg.strip() == '' or pkg.startswith("#"):
                continue
            if pkg.startswith("-e"):
                continue
                try:
                    p = pkg.split("#egg=")[1]
                    dependenses += [p, ]
                except:
                    continue
            else:
                dependenses += [pkg, ]
    return dependenses


setup(
    name="django-extra-cbv",
    version=version,
    description="Extra class based views for Django",
    long_description=read('README.md'),
    keywords="cbv, class based views",
    author="Alex Kamedov",
    author_email="alex@kamedov.ru",
    url="https://github.com/alekam/django-extra-cbv",
    license="New BSD License",
    platforms=["any"],
    classifiers=["Development Status :: 4 - Beta",
                 "Environment :: Web Environment",
                 "Framework :: Django",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Topic :: Utilities"],
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=get_requires_list('requirements.txt'),
    include_package_data=True,
)
