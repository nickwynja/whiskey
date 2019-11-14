import os
from whiskey import app, assets
from flask_assets import Bundle


app.static_folder = app.config['STATIC_FOLDER']

_sass = Bundle(

    '../styles/*.scss',

    filters='libsass',
    depends=(
        '../styles/*.scss'
    ),
    output='gen/sass.%(version)s.css'
)

all_css = Bundle(

    '../styles/*.css',

    _sass,
    filters='cssmin',
    output="gen/all.%(version)s.css"
)

assets.register('css_all', all_css)

for files in os.walk('/src/js/'):
    if files:
        js = Bundle('../src/js/*.js',
                    filters='jsmin',
                    output='gen/bundle.%(version)s.js'
                    )
        assets.register('js_all', js)
