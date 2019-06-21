import os
from whiskey import app, assets
from flask_assets import Bundle


app.static_folder = app.config['STATIC_FOLDER']

_sass = Bundle(

    '../../_global/styles/*.scss',
    '../styles/*.scss',

    filters='libsass',
    depends=(
        '../../_global/styles/*.scss',
        '../styles/*.scss'
    ),
    output='gen/sass.%(version)s.css'
)

all_css = Bundle(

    '../../_global/styles/*.css',
    '../styles/*.css',

    _sass,
    filters='cssmin',
    output="gen/all.%(version)s.css"
)

assets.register('css_all', all_css)

for files in os.walk('sites/%s/src/js/' % app.config['SITE_NAME']):
    if files:
        js = Bundle('../src/js/*.js',
                    filters='jsmin',
                    output='gen/bundle.%(version)s.js'
                    )
        assets.register('js_all', js)
