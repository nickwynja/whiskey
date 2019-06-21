from flask import render_template, abort, send_from_directory
import os
import re
from whiskey import app, flatpages

from whiskey import markdown, helpers


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
        for idx, p in enumerate(featured_posts):
            md = ("<div class=\"markdown-wrapper\""
                  "markdown=\"span\">%s</div>" % p['description'])
            setattr(featured_posts[idx],
                    'description',
                    markdown(md)
                    )
        updates = helpers.get_updates(True)
        latest_update = updates[-1] if updates else None
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
    if name == "resume":
        if ext == "pdf":
            return send_from_directory(
                app.config['CONTENT_PATH'], '%s.%s' % ("resume", "pdf")
            )
        elif ext == "md":
            file = '{}/{}.md'.format(app.config['CONTENT_PATH'], name)
            return helpers.get_flatfile_or_404(file)
        else:
            # Handle special alignment cases for resume
            p = flatpages.get(name)
            p.body = re.sub('\\\\Date {(.*?)}', r"<time>\g<1></time>", p.body)
            return render_template('page.html', post=p, site=app.config)
    elif ext == "html":
        p = flatpages.get(name)
        if helpers.is_published(p):
            return render_template('page.html', post=p, site=app.config)
        else:
            abort(404)
    elif ext == "txt":
        file = "./%s/%s.txt" % (app.config['CONTENT_PATH'], name)
        return helpers.get_flatfile_or_404(file)
    elif ext == "md":
        file = '{}/{}.md'.format(app.config['CONTENT_PATH'], name)
        return helpers.get_flatfile_or_404(file)
    else:
        abort(404)


if app.config['SITE_STYLE'] in ("blog", "hybrid"):

    @app.route("/updates.html")
    def updates():
        updates = reversed(helpers.get_updates())
        date_ordered = {}
        for u in updates:
            d = u['date'].strftime('%Y-%m-%d')
            if d in date_ordered:
                date_ordered[d].insert(0, u)
            else:
                date_ordered[d] = [u]
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
    return render_template('404.html', site=app.config), 404
