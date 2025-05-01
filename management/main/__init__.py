"""
This file is the package initializer for the `management.main` module.
It ensures that the Celery application instance is imported and available
as `celery_app` when the package is imported. The `__all__` variable
restricts what is exported when `from management.main import *` is used.
"""

from __future__ import absolute_import, unicode_literals
from main.celery import app as celery_app

__all__ = ("celery_app",)
