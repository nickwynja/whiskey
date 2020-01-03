from flask import render_template, abort, send_from_directory
import os
import re
from whiskey import app, flatpages

from whiskey import helpers


@app.context_processor
def inject_mode():
    return dict(published=app.config['PUBLISH_MODE'])


@app.route("/")
def index():
    if app.config['SITE_STYLE'] == "static":
        p = flatpages.get("index")
        return render_template('index_static.html', post=p, site=app.config)
    elif app.config['SITE_STYLE'] == "hybrid":
        page = flatpages.get("index")
        fp = helpers.get_featured_posts()
        ap = helpers.get_posts()
        featured_posts = fp[:int(app.config['FEATURED_POSTS_COUNT'])]
        all_posts = ap[:int(app.config['RECENT_POSTS_COUNT'])]
        updates = helpers.get_updates(True)
        latest_update = updates[-1] if updates else None
        latest_update['html'] = helpers.pandoc_markdown(latest_update['text'])
        return render_template('index_hybrid.html',
                               post=page,
                               directory=app.config['POST_DIRECTORY'],
                               featured_posts=featured_posts,
                               all_posts=all_posts,
                               latest_update=latest_update,
                               site=app.config
                               )
    elif app.config['SITE_STYLE'] == "blog":
        p = helpers.get_featured_posts()
        ap = helpers.get_posts()
        featured_posts = p[:int(app.config['FEATURED_POSTS_COUNT'])]
        all_posts = ap[:int(app.config['RECENT_POSTS_COUNT'])]
        return render_template('index_list.html',
                               directory=app.config['POST_DIRECTORY'],
                               featured_posts=featured_posts,
                               all_posts=all_posts, site=app.config)
    else:
        abort(404)


@app.route('/<int:year>/<int:month>/<name>.<ext>')
@app.route('/<dir>/<name>.<ext>')
def nested_content(name, ext, dir=None, year=None, month=None):
    if dir:
        path = '{}/{}'.format(dir, name)
    else:
        dir = app.config['POST_DIRECTORY']
        if year and month:
            month = "{:02d}".format(month)
            path = '%s/%s/%s/%s' % (dir, year, month, name)
    if ext == "html":
        if os.path.isfile('%s/%s.%s' % (
                app.config['CONTENT_PATH'], path, ext)):
            return send_from_directory('%s/%s' % (
                app.config['CONTENT_PATH'], dir), '%s.%s' % (name, ext))
        else:
            page = flatpages.get(path)
            if helpers.is_published_or_draft(page):
                if dir == app.config['POST_DIRECTORY']:
                    return render_template('post.html', post=page,
                                           directory=dir, ext=ext,
                                           site=app.config)
                else:
                    if ('templateType' in page.meta
                            and page.meta['templateType'] == "post"):
                        template_type = "post.html"
                    else:
                        template_type = "page.html"

                    return render_template(template_type, post=page,
                                           directory=dir, ext=ext,
                                           site=app.config)
            else:
                abort(404)
    elif ext == "md":
        file = '{}/{}.md'.format(app.config['CONTENT_PATH'], path)
        return helpers.get_flatfile_or_404(file)
    else:
        abort(404)


@app.route('/<name>.<ext>')
def page(name, ext):
    if ext == "html":
        p = flatpages.get(name)
        if helpers.is_published(p):
            if 'footer' in p.meta:
                setattr(p, 'footer', helpers.pandoc_markdown(p.meta['footer']))
            return render_template('page.html', post=p, site=app.config)
        else:
            abort(404)
    elif ext in ['txt', 'md']:
        file = '{}/{}.{}'.format(app.config['CONTENT_PATH'], name, ext)
        return helpers.get_flatfile_or_404(file)
    elif ext == "pdf":
        return send_from_directory(
            app.config['CONTENT_PATH'], '%s.%s' % (name, "pdf")
        )
    else:
        abort(404)


if app.config['SITE_STYLE'] in ("blog", "hybrid"):

    @app.route("/updates.html")
    def updates():
        updates = reversed(helpers.get_updates())
        date_ordered = {}
        for u in updates:
            u['html'] = (u['html'] if 'html' in u
                         else helpers.pandoc_markdown(u['text']))
            d = u['date'].strftime('%Y-%m-%d')
            if d in date_ordered and u.get('featured') is True:
                date_ordered[d].setdefault('featured', []).insert(
                    len(date_ordered[d]['featured']), u
                )
            elif d in date_ordered and u.get('featured') is not True:
                date_ordered[d].setdefault('regular', []).insert(
                    0, u
                )
            elif u.get('featured') is True:
                date_ordered[d] = {'featured': [u]}
            else:
                date_ordered[d] = {'regular': [u]}
        return render_template('updates.html', updates=date_ordered,
                               site=app.config)

    @app.route("/archive.html")
    @app.route("/%s/" % app.config['POST_DIRECTORY'])
    def archive():
        posts = helpers.get_posts()
        return render_template('archive.html', posts=posts,
                               directory=app.config['POST_DIRECTORY'],
                               site=app.config)

    from whiskey import feeds


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', site=app.config)
