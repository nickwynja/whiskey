import yaml
import glob
import os
import tarfile
import pypandoc
import datetime
from flask import abort
from flask_babel import format_datetime
from whiskey import app, flatpages
from pathlib import Path


def get_posts():
    '''returns list of published posts ordered newest first'''
    posts = [p for p in flatpages
             if (p.path.startswith(app.config['POST_DIRECTORY'])
                 and is_published(p)
                 and not is_hidden(p))
             ]
    posts.sort(key=lambda item: item['date'], reverse=True)
    for idx, p in enumerate(posts):
        slug = p.path.replace('{}/'.format(app.config['POST_DIRECTORY']), '')
        setattr(posts[idx], 'slug', slug)
    return posts


def get_featured_posts():
    '''returns list of posts marked `featured` in post metadata'''
    all_posts = get_posts()
    return [p for p in all_posts if 'featured' in p.meta and p.meta['featured']
            is True]


def pandoc_markdown(md):
    return pypandoc.convert_text(
        md,
        'html',
        format='md',
        filters=app.config['PANDOC_FILTERS']
    )

def get_latest_log():
    updates = []
    file = sorted(glob.glob(f"{app.config['DATA_PATH']}/log/*"))[-1]

    with open(file, 'r') as f:
        date = datetime.datetime.strptime(Path(f.name).stem, '%Y%m%d%H%M%S%z')
        content = f.read()
        if Path(f.name).suffix == ".md":
            entry = pypandoc.convert_text(content, 'html', format='md')
        else:
            entry = l

    return (date,entry)

def get_updates(featured=False):
    updates = []
    featured_updates = []
    files = sorted(glob.glob(f"{app.config['DATA_PATH']}/updates/*.yaml"))

    for file in files:
        with open(file, 'r') as stream:
            try:
                y = yaml.safe_load(stream)
                y['filename'] = file
                if y.get('published', True) is True:
                    updates.append(y)
                if y.get('featured', False) is True:
                    featured_updates.append(y)
            except yaml.YAMLError as exc:
                print(exc)

    if featured:
        return featured_updates

    return updates


def format_date(value):
    '''takes a date obj and returns in November 22, 2016 format'''
    return format_datetime(value, 'LLLL d, yyyy')


def format_month_year(value):
    '''takes a date obj and returns in November 2016 format'''
    return format_datetime(value, 'LLLL yyyy')

def format_date_tz(value):
    ast = value.astimezone()
    date = ast.strftime("%B %-d, %Y")
    time = ast.strftime("%H:%M %Z")
    return f"<span class='date'>{date}</span> <span class='time'>{time}</span>"

def is_published(post):
    '''returns True/False based on `published` metadata in post'''
    return post and 'published' in post.meta and post.meta['published'] is True


def is_hidden(post):
    '''returns True/False based on `hidden` metadata in post'''
    return post and 'hidden' in post.meta and post.meta['hidden'] is True


def is_published_or_draft(post):
    '''returns True/False based on `published` metadata in post'''
    if (post is not None
            and (post.meta.get('published', False) is True
                 or post.meta.get('status', "").lower() == "draft"
                 )):
        return post


def is_draft(post):
    '''returns True/False based on `published` metadata in post'''
    if (post is not None
            and (('published' in post.meta
                  and post.meta['published'] is False)
                 or ('status' in post.meta
                     and post.meta['status'].lower() == "draft")
                 or ('published' not in post.meta))):
        return post


def list_files_in_dir(dir, root_only=None):
    pages = []
    files_to_yield = []
    if root_only:
        files = glob.glob("%s/*.md" % dir)
        files.extend(glob.glob("%s/*.txt" % dir))
        files.extend(glob.glob("%s/*.pdf" % dir))
    else:
        files = glob.glob("%s/**/*.md" % dir, recursive=True)
        files.extend(glob.glob("%s/**/*.txt" % dir, recursive=True))
        files.extend(glob.glob("%s/**/*.epub" % dir, recursive=True))
        files.extend(glob.glob("%s/**/*.pdf" % dir, recursive=True))
    for file in files:
        files_to_yield.append(file.replace('%s/' % dir, ''))
    for page in files_to_yield:
        path, filename = os.path.split(page)
        name, extension = filename.split('.')[-2:]
        if extension == 'md':
            if path:
                p = flatpages.get("%s/%s" % (path, name))
            elif name != "index":  # Don't include or it'll override actual
                p = flatpages.get("%s" % (name))
            else:
                p = None
            if p and is_published(p):
                if ('POST_LINK_STYLE' in app.config
                        and app.config['POST_LINK_STYLE'] == "date"
                        and path.startswith(app.config['POST_DIRECTORY'])):
                    path = path.replace("%s/" % app.config['POST_DIRECTORY'],
                                        '')
                pages.append({'name': name, 'dir': path, 'ext': 'html'})
                pages.append({'name': name, 'dir': path, 'ext': 'md'})
        else:
            pages.append({'name': name, 'dir': path, 'ext': extension})
    return pages


def get_flatfile_or_404(file):
    if os.path.isfile(file):
        with open(file, 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        abort(404)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
