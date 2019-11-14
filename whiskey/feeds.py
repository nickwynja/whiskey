from whiskey import app, flatpages, helpers
import urllib.parse
from flask import url_for
from pytz import timezone
from html.parser import HTMLParser
from werkzeug.contrib.atom import AtomFeed


@app.route('/feed.atom')
def feed():
    h = HTMLParser()
    tz = app.config['TIMEZONE']
    feed = AtomFeed('%s' % app.config['TITLE'],
                    feed_url=app.config['BASE_URL'] + url_for('feed'),
                    subtitle=app.config.get('DESCRIPTION', ""),
                    author=app.config.get('AUTHOR', ""),
                    url=app.config['BASE_URL'])
    posts = helpers.get_posts()
    for p in posts:
        post = flatpages.get(p.path)
        if ('POST_LINK_STYLE' in app.config
                and app.config['POST_LINK_STYLE'] == "date"):
            url = "%s/%s" % (app.config['BASE_URL'], p.slug)
        else:
            url = "{}{}".format(
                app.config['BASE_URL'],
                url_for('nested_content', name=p.slug,
                        dir=app.config['POST_DIRECTORY'], ext='html'))
        feed.add(p.meta['title'],
                 content_type='html',
                 author=p.meta.get('author', app.config.get('AUTHOR', "")),
                 url=url,
                 updated=timezone(tz).localize(
                     p.meta.get('updated', p.meta['date'])),
                 published=timezone(tz).localize(p.meta['date']),
                 summary=h.unescape(
                     post.meta.get('description', '')),
                 content=h.unescape(post.html)
                 )
    return feed.get_response()


@app.route('/updates.atom')
def feed_updates():
    h = HTMLParser()
    tz = app.config['TIMEZONE']
    feed = AtomFeed('Updates from %s' % app.config['TITLE'],
                    feed_url="{}{}".format(
                        app.config['BASE_URL'],
                        url_for('feed_updates')),
                    subtitle=app.config.get('DESCRIPTION', ""),
                    author=app.config.get('AUTHOR', ""),
                    url=app.config['BASE_URL'])
    updates = helpers.get_updates()
    for u in updates:
        feed.add(u['date'],
                 content_type='html',
                 author=app.config.get('AUTHOR', ""),
                 url="{}/updates.html#{}".format(
                     app.config['BASE_URL'],
                     u['date'].strftime('%Y-%m-%d_%H%M%S')),
                 updated=timezone(tz).localize(u['date']),
                 published=timezone(tz).localize(u['date']),
                 content="%s" % h.unescape(helpers.pandoc_markdown(u['text']))
                 )
    return feed.get_response()


@app.route('/all.atom')
def feed_all():
    h = HTMLParser()
    tz = app.config['TIMEZONE']
    feed = AtomFeed('All posts from %s' % app.config['TITLE'],
                    feed_url=app.config['BASE_URL'] + url_for('feed_all'),
                    subtitle=app.config.get('DESCRIPTION', ""),
                    author=app.config.get('AUTHOR', ""),
                    url=app.config['BASE_URL'])
    updates = helpers.get_updates()
    for u in updates:
        feed.add(u['date'],
                 content_type='html',
                 author=app.config.get('AUTHOR', ""),
                 url="{}/updates.html#{}".format(
                     app.config['BASE_URL'],
                     u['date'].strftime('%Y-%m-%d_%H%M%S')),
                 updated=timezone(tz).localize(u['date']),
                 published=timezone(tz).localize(u['date']),
                 content="%s" % h.unescape(helpers.pandoc_markdown(u['text']))
                 )
    posts = helpers.get_posts()
    for p in posts:
        post = flatpages.get(p.path)
        if ('POST_LINK_STYLE' in app.config
                and app.config['POST_LINK_STYLE'] == "date"):
            url = "%s/%s" % (app.config['BASE_URL'], p.slug)
        else:
            url = "{}{}".format(
                app.config['BASE_URL'],
                url_for('nested_content', name=p.slug,
                        dir=app.config['POST_DIRECTORY'], ext='html'))
        md = ("<div markdown=\"block\">"
              "<b>{}</b>&nbsp;&bull;&nbsp;<span>{}</span>&nbsp;"
              "<a href=\"{}\">{}</a></div>".format(
                  p.meta['title'],
                  post.meta.get('description', ""),
                  url,
                  app.config['BASE_NAME']))
        feed.add(p.meta['date'],
                 content_type='html',
                 author=p.meta.get('author', app.config.get('AUTHOR', "")),
                 url=url,
                 updated=timezone(tz).localize(
                     p.meta.get('updated', p.meta['date'])),
                 published=timezone(tz).localize(p.meta['date']),
                 content=h.unescape(helpers.pandoc_markdown(md))
                 )
    return feed.get_response()
