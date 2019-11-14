from whiskey import app
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

FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = app.config['CONTENT_PATH']
FREEZER_DESTINATION = app.config['BUILD_PATH']
FREEZER_RELATIVE_URLS = True
FREEZER_IGNORE_MIMETYPE_WARNINGS = True
FREEZER_STATIC_IGNORE = ['*.DS_Store']
