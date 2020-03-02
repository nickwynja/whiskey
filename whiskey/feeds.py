from whiskey import app, flatpages, helpers
import urllib.parse
from flask import url_for, Response
from pytz import timezone
from feedgen.feed import FeedGenerator


@app.route('/feed.rss')
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
        entry.updated(timezone(tz).localize(p.meta.get('updated', p.meta['date'])))
        entry.published(timezone(tz).localize(p.meta['date']))
        entry.description(post.meta.get('description', ''))
        # It takes a while to render all of the HTML here but
        # then at least it is in memory and the rest of the
        # build process goes quickly. The rendering has to
        # happen anyway so there isn't any performance increase
        # by not including the full HTML here in content.
        entry.content(post.html)

    return Response(feed.rss_str(pretty=True), mimetype="application/rss+xml")


@app.route('/updates.rss')
def feed_updates():
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
        entry.id(u['date'].strftime("%Y-%m-%d %H:%M:%S %z"))
        entry.author(name=app.config.get('AUTHOR', ""))
        entry.link(href="{}/updates.html#{}".format(
                         app.config['BASE_URL'],
                         u['date'].strftime('%Y-%m-%d_%H%M%S')))
        entry.updated(timezone(tz).localize(u['date']))
        entry.published(timezone(tz).localize(u['date']))
        entry.content("%s" % (
                         u['html'] if 'html' in u
                         else helpers.pandoc_markdown(u['text'])))
    return Response(feed.rss_str(pretty=True), mimetype="application/rss+xml")


@app.route('/all.rss')
def feed_all():
    tz = app.config['TIMEZONE']
    feed = FeedGenerator()
    feed.title('All content from %s' % app.config['TITLE'])
    feed.link(href=app.config['BASE_URL'] + url_for('feed_all'), rel='self')
    feed.subtitle(app.config.get('DESCRIPTION', ""))
    feed.author(name=app.config.get('AUTHOR', ""))
    feed.link(href=app.config['BASE_URL'], rel='alternate')

    updates = helpers.get_updates()
    posts = helpers.get_posts()
    all_items = []

    for u in updates:
        all_items.append({
            'title': u['date'].strftime("%Y-%m-%d %H:%M:%S %z"),
            'author': app.config.get('AUTHOR', ""),
            'link': "{}/updates.html#{}".format(
                         app.config['BASE_URL'],
                         u['date'].strftime('%Y-%m-%d_%H%M%S')),
            'updated': timezone(tz).localize(u['date']),
            'published': timezone(tz).localize(u['date']),
            'content': "%s" % (
                         u['html'] if 'html' in u
                         else helpers.pandoc_markdown(u['text']))
        })

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
        all_items.append({
            'title': p.meta['date'].strftime("%Y-%m-%d %H:%M:%S %z"),
            'author': p.meta.get('author', app.config.get('AUTHOR', "")),
            'link': url,
            'updated': timezone(tz).localize(p.meta.get('updated', p.meta['date'])),
            'published': timezone(tz).localize(p.meta['date']),
            'content': html
        })

    for i in sorted(all_items, key=lambda k: k['title']):
        entry = feed.add_entry()
        entry.title(i['title'])
        entry.guid(guid=i['link'], permalink=True)
        entry.author(name=i['author'])
        entry.link(href=i['link'])
        entry.updated(i['updated'])
        entry.published(i['published'])
        entry.description(i['content'])

    return Response(feed.rss_str(pretty=True), mimetype="application/rss+xml")
