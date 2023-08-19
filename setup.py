#!/usr/bin/env python
from setuptools import setup, find_packages, convert_path

NAME  = "plex_discord_notify"
DESC  = "Package for catching Plex webhooks and publishing to Discord"
URL   = ""
AUTH  = "Kyle R. Wodzicki"
EMAIL = "krwodzicki@gmail.com"

main_ns  = {}
ver_path = convert_path( "{}/version.py".format(NAME) )
with open(ver_path) as ver_file:
  exec(ver_file.read(), main_ns)

INSTALL_REQUIRES = [
    "requests",
]

SCRIPTS = [
    'bin/plex_discord_notify',
]

if __name__ == "__main__":
    setup(
        name                = NAME,
        description         = DESC,
        url                 = URL,
        author              = AUTH,
        author_email        = EMAIL,
        version             = main_ns['__version__'],
        packages            = find_packages(),
        install_requires    = INSTALL_REQUIRES,
        scripts             = SCRIPTS,
        zip_safe            = False,
    )
