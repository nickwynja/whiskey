from whiskey import app
from whiskey.formatter import poetic_formatter
import mkdcomments
import mdx_poetic
import os

site_path = '%s/sites/%s' % (os.path.dirname(app.root_path),
                             os.environ['WHISKEY_SITE'])
# Set defaults which can be overriden in site.conf
app.config.update(
    TIMEZONE='US/Eastern',
    FEATURED_POSTS_COUNT=3,
    RECENT_POSTS_COUNT=10,
)
app.config.from_pyfile('%s/site.conf' % site_path)
app.config.update(
    SITE_NAME=os.environ['WHISKEY_SITE'],
    CONTENT_PATH='%s/content' % site_path,
    BUILD_PATH='%s/build' % site_path,
    STATIC_FOLDER='%s/static' % site_path,
    TEMPLATE_PATH='%s/templates' % site_path,
    PUBLISH_MODE=False
)

app.config['MARKDOWN_EXTENSIONS'] = [
    'smarty',
    'pymdownx.extrarawhtml',
    mdx_poetic.PoeticExtension()

]

FLATPAGES_AUTO_RELOAD = True
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = app.config['CONTENT_PATH']
TEMPLATES_AUTO_RELOAD = True
FREEZER_DESTINATION = app.config['BUILD_PATH']
FREEZER_IGNORE_404_NOT_FOUND = True
FREEZER_IGNORE_404_FOR_URLS = ['/404.html']
FREEZER_RELATIVE_URLS = True
FREEZER_IGNORE_MIMETYPE_WARNINGS = True

FLATPAGES_MARKDOWN_EXTENSIONS = [
    'footnotes',
    'toc',
    'extra',
    'smarty',
    'sane_lists',
    'pymdownx.critic',
    mkdcomments.CommentsExtension(),
    'pymdownx.superfences',
]

FLATPAGES_EXTENSION_CONFIGS = {
    'footnotes': {
        'UNIQUE_IDS': 'True'
    },
    "pymdownx.superfences": {
        "custom_fences": [{
            "name": "poem",
            "class": "mdx-poem",
            "format": poetic_formatter
        }, {
            "name": "poemItalic",
            "class": "mdx-poem italic",
            "format": poetic_formatter
        }]
    }
}
