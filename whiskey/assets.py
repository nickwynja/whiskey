import os
import sass
import rcssmin
from whiskey import app, assets
from flask_assets import Bundle


@app.context_processor
def inject_dict_for_all_templates():
    css = ""
    try:
        with open('src/styles/style.scss', 'r') as scss:
            css = sass.compile(string=scss.read())
        return dict(cssmin=rcssmin.cssmin(css))
    except BaseException:
        return dict(cssmin="")


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

for files in os.walk('src/js/'):
    if files:
        js = Bundle('../js/*.js',
                    filters='jsmin',
                    output='gen/bundle.%(version)s.js'
                    )
        assets.register('js_all', js)
