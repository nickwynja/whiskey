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
FlatPagesPandoc("markdown", app)
freezer = Freezer(app)

import whiskey.assets
import whiskey.templates
import whiskey.views
import whiskey.commands
from whiskey import helpers, freeze
