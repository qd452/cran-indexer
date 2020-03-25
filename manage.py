# manage.py


import unittest

import redis
from flask.cli import FlaskGroup

from webapp import create_app, celery, mongo
from webapp.model import create_mongo_index

app = create_app()
create_mongo_index(mongo)
cli = FlaskGroup(create_app=create_app)


@cli.command()
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('app/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    cli()
# !/usr/bin/env python
# -*- coding: utf-8 -*-
