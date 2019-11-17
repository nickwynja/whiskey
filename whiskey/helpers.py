import yaml
import glob
import os
import tarfile
import pypandoc
from flask import abort
from flask_babel import format_datetime
from whiskey import app, flatpages


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
        filters=['poetic']
    )


def get_updates(featured=False):
    f = "%s/updates.yaml" % app.config['DATA_PATH']

    if os.path.exists(f):
        with open(f, 'r') as stream:
            try:
                if featured:
                    updates = [u for u in yaml.safe_load(stream)
                               if u.get('featured', False) is True]
                else:
                    updates = yaml.safe_load(stream)
                return updates
            except yaml.YAMLError as exc:
                print(exc)
            except EnvironmentError:
                return ""
    else:
        return []


def format_date(value):
    '''takes a date obj and returns in November 22, 2016 format'''
    return format_datetime(value, 'LLLL d, yyyy')


def format_month_year(value):
    '''takes a date obj and returns in November 2016 format'''
    return format_datetime(value, 'LLLL yyyy')


def is_published(post):
    '''returns True/False based on `published` metadata in post'''
    return post and 'published' in post.meta and post.meta['published'] is True


def is_hidden(post):
    '''returns True/False based on `hidden` metadata in post'''
    return post and 'hidden' in post.meta and post.meta['hidden'] is True


def is_published_or_draft(post):
    '''returns True/False based on `published` metadata in post'''
    if (post is not None
            and (('published' in post.meta and post.meta['published'] is True)
                 or ('status' in post.meta
                     and post.meta['status'].lower() == "draft")
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
