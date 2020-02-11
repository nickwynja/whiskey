from whiskey import app, flatpages, helpers
import urllib.parse
from flask import url_for, Response
from pytz import timezone
from html.parser import HTMLParser
from feedgen.feed import FeedGenerator


@app.route('/feed.rss')
def feed():
    h = HTMLParser()
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
        entry.author(name=p.meta.get('author', app.config.get('AUTHOR', "")))
        entry.link(href=url)
        entry.updated(timezone(tz).localize(p.meta.get('updated', p.meta['date'])))
        entry.published(timezone(tz).localize(p.meta['date']))
        entry.description(h.unescape(
            post.meta.get('description', '')))
        # It takes a while to render all of the HTML here but
        # then at least it is in memory and the rest of the
        # build process goes quickly. The rendering has to
        # happen anyway so there isn't any performance increase
        # by not including the full HTML here in content.
        entry.content(h.unescape(post.html))

    return Response(feed.rss_str(pretty=True), mimetype="text/xml")


@app.route('/updates.rss')
def feed_updates():
    h = HTMLParser()
    tz = app.config['TIMEZONE']

    feed = FeedGenerator()
    feed.title('Updates from %s' % app.config['TITLE'])
    feed.link(href=app.config['BASE_URL'] + url_for('feed_updates'), rel='self')
    feed.subtitle(app.config.get('DESCRIPTION', ""))
    feed.author(name=app.config.get('AUTHOR', ""))
    feed.link(href=app.config['BASE_URL'], rel='alternate')

    updates = helpers.get_updates()
    for u in updates:
        entry = feed.add_entry()
        entry.title(u['date'].strftime("%Y-%m-%d %H:%M:%S %z"))
        entry.author(name=app.config.get('AUTHOR', ""))
        entry.link(href="{}/updates.html#{}".format(
                         app.config['BASE_URL'],
                         u['date'].strftime('%Y-%m-%d_%H%M%S')))
        entry.updated(timezone(tz).localize(u['date']))
        entry.published(timezone(tz).localize(u['date']))
        entry.content("%s" % (
                         u['html'] if 'html' in u
                         else h.unescape(helpers.pandoc_markdown(u['text']))))
    return Response(feed.rss_str(pretty=True), mimetype="text/xml")


@app.route('/all.rss')
def feed_all():
    h = HTMLParser()
    tz = app.config['TIMEZONE']
    feed = FeedGenerator()
    feed.title('All posts from %s' % app.config['TITLE'])
    feed.link(href=app.config['BASE_URL'] + url_for('feed_all'), rel='self')
    feed.subtitle(app.config.get('DESCRIPTION', ""))
    feed.author(name=app.config.get('AUTHOR', ""))
    feed.link(href=app.config['BASE_URL'], rel='alternate')

    updates = helpers.get_updates()

    for u in updates:
        entry = feed.add_entry()
        entry.title(u['date'].strftime("%Y-%m-%d %H:%M:%S %z"))
        entry.author(name=app.config.get('AUTHOR', ""))
        entry.link(href="{}/updates.html#{}".format(
                         app.config['BASE_URL'],
                         u['date'].strftime('%Y-%m-%d_%H%M%S')))
        entry.updated(timezone(tz).localize(u['date']))
        entry.published(timezone(tz).localize(u['date']))
        entry.content("%s" % (
                         u['html'] if 'html' in u
                         else h.unescape(helpers.pandoc_markdown(u['text']))))

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
        html = ("<b>{}</b>&nbsp;&bull;&nbsp;<span>{}</span>&nbsp;"
                "<a href=\"{}\">{}</a>".format(
                    p.meta['title'],
                    post.meta.get('description', ""),
                    url,
                    app.config['BASE_NAME']))
        entry = feed.add_entry()
        entry.title(p.meta['date'].strftime("%Y-%m-%d %H:%M:%S %z"))
        entry.author(name=p.meta.get('author', app.config.get('AUTHOR', "")))
        entry.link(href=url)
        entry.updated(timezone(tz).localize(p.meta.get('updated', p.meta['date'])))
        entry.published(timezone(tz).localize(p.meta['date']))
        entry.description(h.unescape(
            post.meta.get('description', '')))
        entry.content(h.unescape(html))

    return Response(feed.rss_str(pretty=True), mimetype="text/xml")
