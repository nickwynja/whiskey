from flask import render_template, abort, send_from_directory
import os
import re
import mimetypes
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
        if updates:
            latest_update = updates[-1] if updates else None
            latest_update['html'] = (latest_update['html'] if 'html' in
                                     latest_update else
                                     helpers.pandoc_markdown(
                                         latest_update['text']))
        else:
            latest_update = ""
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
    elif ext in ["md", "pdf", "epub"]:
        path = "{}/{}".format(app.config['CONTENT_PATH'], dir)
        filename = "{}.{}".format(name, ext)
        file = '{}/{}'.format(path, filename)
        mime = mimetypes.guess_type(file)[0]
        if mime in ["application/pdf", "application/epub+zip"]:
            return send_from_directory(path, filename, as_attachment=True)
        else:
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
    elif name == "resume" and ext == "pdf":
        p = flatpages.get(name)
        import pypandoc
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        resume_html =  pypandoc.convert_file(
             "%s/resume.md" % app.config['CONTENT_PATH'],
            'html',
            format='md'
        )

        font_config = FontConfiguration()
        header = f"""
        <h1>{app.config['AUTHOR']}</h1>
        <div class="header">
            <a href="https://{p.meta['website']}">{p.meta['website']}</a>
            <span class="align-right">{p.meta['location']}</span>
        </div>
        <div class="header">
            <a href="mailto:{p.meta['email']}">{p.meta['email']}</a>
            <span class="align-right">{p.meta['phone']}</span>
        </div>
        """
        html = HTML(string=f"{header}{resume_html}")
        css = CSS(string="""
        body {
          font-size: 69%;
          font-family: "Open Sans";
          line-height: 1.4;
          text-align: justify;
          text-justify: inter-word;
        }

        h1 { margin-bottom: 0; }

        ul {
            padding-left: 25px;
        }

        ul ul {
            list-style-type: disc;
        }

        .header { color: grey; }
        .header a { color: grey; text-decoration: none; }

        p a { color: black; text-decoration: none; }

        .align-right { float: right; }
        @page { size: letter; margin: 1cm 1.5cm 1cm 1cm;  }
                """)

        html.write_pdf(
            f"{app.config['CONTENT_PATH']}/{name}.pdf",
            stylesheets=[css],
                  font_config=font_config
                )
        return send_from_directory(
            app.config['CONTENT_PATH'], '%s.%s' % (name, "pdf")
        )
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
            if u.get('text'):
                app.logger.debug(f"{os.path.basename(u['filename'])} is \
converted from markdown which slows down page load time")
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
    @app.route("/%s/index.html" % app.config['POST_DIRECTORY'])
    def archive():
        posts = helpers.get_posts()
        return render_template('archive.html', posts=posts,
                               directory=app.config['POST_DIRECTORY'],
                               site=app.config)

    from whiskey import feeds


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', site=app.config)


@app.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html', site=app.config)
