#!/usr/bin/env python3
"""Whiskey makes writing happen."""

import os
from flask import Flask
from flask_frozen import Freezer
from flask_assets import Environment
from flask_flatpages import FlatPages
from flask_babel import Babel
from whiskey.flatpandoc import FlatPagesPandoc

app = Flask(__name__)
app.config.from_pyfile('settings.py')


assets = Environment(app)
babel = Babel(app)
flatpages = FlatPages(app)
FlatPagesPandoc(app.config['PANDOC_MD_FORMAT'],
                app,
                pandoc_args=app.config['PANDOC_ARGS'],
                filters=app.config['PANDOC_FILTERS']
                )
freezer = Freezer(app)

import whiskey.assets
import whiskey.templates
import whiskey.views
import whiskey.commands
from whiskey import helpers, freeze
