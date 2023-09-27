from whiskey import app, flatpages, helpers
import urllib.parse
import glob
import datetime
import os
import pypandoc
from flask import url_for, Response, redirect
from pytz import timezone
from feedgen.feed import FeedGenerator
from pathlib import Path


@app.route('/rss')
@app.route('/feed.rss')
def feed_redirect():
    return redirect(url_for('feed'), code=301)

@app.route('/feed.xml')
def feed():
    tz = app.config['TIMEZONE']
    posts = helpers.get_posts()

    feed = FeedGenerator()
    feed.title('%s' % app.config['TITLE'])
    feed.link(href=app.config['BASE_URL'] + url_for('feed'), rel='self')
    feed.subtitle(app.config.get('DESCRIPTION', ""))
    feed.author(name=app.config.get('AUTHOR', ""))
    feed.link(href=app.config['BASE_URL'], rel='alternate')

    for p in posts[:10]:
        post = flatpages.get(p.path)
        if ('POST_LINK_STYLE' in app.config
                and app.config['POST_LINK_STYLE'] == "date"):
            url = "%s/%s" % (app.config['BASE_URL'], p.slug)
        else:
            url = "{}{}".format(
                app.config['BASE_URL'],
                url_for('nested_content', name=p.slug,
                        dir=app.config['POST_DIRECTORY'], ext='html'))

        entry = feed.add_entry()
        entry.title(p.meta['title'])
        entry.guid(guid=url, permalink=True)
        entry.author(name=p.meta.get('author', app.config.get('AUTHOR', "")))
        entry.link(href=url)
        entry.updated(timezone(tz).localize(
            p.meta.get('updated', p.meta['date'])))
        entry.published(timezone(tz).localize(p.meta['date']))
        entry.description(post.meta.get('description', ''))
        # It takes a while to render all of the HTML here but
        # then at least it is in memory and the rest of the
        # build process goes quickly. The rendering has to
        # happen anyway so there isn't any performance increase
        # by not including the full HTML here in content.
        entry.content(post.html)

    return Response(feed.rss_str(pretty=True), mimetype="application/rss+xml")

@app.route('/log.xml')
def log():
    feed = FeedGenerator()
    feed.title(f"{app.config.get('AUTHOR')}'s Log")
    feed.link(href=app.config['BASE_URL'] + url_for('log'), rel='self')
    feed.subtitle(app.config.get('DESCRIPTION', ""))
    feed.author(name=app.config.get('AUTHOR', ""))
    feed.id(feed.title())
    feed.link(href=app.config['BASE_URL'], rel='alternate')

    files = sorted(glob.glob("./content/data/log/*"))

    for file in files:
        with open(file) as f:
            d = Path(f.name).stem
            t = datetime.datetime.strptime(d, '%Y%m%d%H%M%S%z')
            l = f.read()

        entry = feed.add_entry()
        entry.id(d.split("-")[0])
        entry.published(t)
        entry.author(name=app.config.get('AUTHOR', ""))
        if Path(f.name).suffix == ".md":
            entry.content(pypandoc.convert_text(l, 'html', format='md'), type="html")
        else:
            entry.content(l, type="html")

    return Response(feed.rss_str(pretty=True), mimetype="application/rss+xml")
