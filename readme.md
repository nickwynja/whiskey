# :tumbler_glass:  Whiskey makes writing happen.

 Whiskey is a static site generator focusing on making writing happen. It gets
 out of the way so you can focus on telling your story.

<details>
<summary><strong>Table of Contents</strong></summary>
<ul>
<li><a href="#features">Features</a></li>
<li><a href="#getting-started">Getting Started</a></li>
  <ul>
    <li><a href="#setup">Setup</a></li>
    <li><a href="#customizing-templates-and-styles">Customizing Templates and Sites</a></li>
    <li><a href="#multiple-sites">Multiple Sites</a></li>
  </ul>
<li><a href="#site-configuration">Site Configuration</a></li>
</ul>
</details>

## Features

* Built around flat Markdown files
* Supports multiple sites with easy per-site configuration
* Built-in publish and backup functionalities
* Command-line driven
* Has an "update" post-style for tweet-like posts
* Generates feeds of regular posts, update posts, and all posts
* Integrate updates with sites like [micro.blog](https://micro.blog)
* Has support for global template and stylesheet inheritance   

To see Whiskey in use, visit [nickwynja.com](https://nickwynja.com).

## Getting Started

Whiskey supports multiple sites, with multiple configuration types.
This will walk you through getting your first Whiskey site up and switching
between multiple sites.

### Setup

1. Run `make venv` to create a virtual environment and install the
   requirements. `virtualenv` is required.
1. In the root of the directory, add a new file called `.flaskenv`. This file will store some information about the app, but won't be version controlled.

        FLASK_APP=whiskey
        FLASK_ENV=development
        WHISKEY_SITE=example

1. Create a new directory in `sites` called `example`.
1. Create a new file called `site.conf` in `sites/example` and add this to
   the file:

        TITLE='Hello World'
        BASE_URL='https://example.com'
        BASE_NAME='example.com'
        SITE_STYLE='static'

1. Now, create a directory in sites called `content` and add the following
   to `content/index.md`:

        ---
        title: Hello World
        ---

        Hi!

1. Run `flask run` and then navigate to
   [127.0.0.1:5000](http://127.0.0.1:5000). You should see a basic page
   that says "Hi!". Easy enough.
1. Let's turn this static site into a blog. In `site.conf`, change
   `SITE_STYLE` from `static` to `blog` and at the bottom of the file add:

        POST_DIRECTORY="posts"

1. Create the directory `sites/example/content/posts`, and add a file called something like `first-post.md` with this content:

        ---
        title: Hello World
        published: True
        date: 2019-06-21 08:52:18
        description: "Nice to meet you."
        ---

        Hope we meet again.

1. Now, stop the `flask` server that's running and re-run it. Reload the page
   and you should now see a simple blog roll. Trying clicking on the blog post.
2. Lets' change `SITE_STYLE` to be `hybrid` now. Re-run the `flask run` command
   again and if reload, you'll now see your content from `index.md` above your
   post blog roll.
1. To "freeze" your site to static files, run `flask build` and look in `sites/example/build`. You should see the generated content of your site.
1. If you have a server and have added the `DEPLOY` information (see below) to your `site.conf`, you can run `flask publish` to publish your static site to your server.

### Customizing Templates and Styles

So far, the example you set up is using the basic templates and styles in
   `sites/_global`. To customize your new site, create directories called
   `templates` and `styles` in your new `sites/example` directory and this will
   override the global templates and append your styles to the stylesheet.
   Override template files by using the same name as the template in the
   `_global` directory.

### Multiple Sites

You can repeat the above steps to create multiple sites within Whiskey. The
default site is set in `.flaskenv` in an environment variable called
`WHISKEY_SITE`. You can change this to the name of the site directory you want
to be default. If you want to work on a different site, located in `/sites/foo`, you can temporarily `export WHISKEY_SITE=foo` and then `flask run` to work on site `foo`, keeping `example` your default.

## Site Configuration

Here is a full example of the options available to configure a site:

```
TITLE='Title of Site'
DESCRIPTION='A description that's used various places.'
BASE_URL='https://example.com'
BASE_NAME='example.com'
NAV=[{"title": "About", "destination": "/about.html"}, {"title": "Contact", "destination": "/contact.html"}]
AUTHOR='Nick Wynja'
TIMEZONE='US/Eastern'
SITE_STYLE='blog'
POST_DIRECTORY='posts'
POST_LINK_STYLE='date'  # if you want a /yyyy/mm/post-slug style URL

FEATURED_POSTS_COUNT=2
RECENT_POSTS_COUNT=100

DEPLOY_HOST=''         # hostname or IP of server to deploy to
DEPLOY_USER=''         # ssh user
DEPLOY_PORT=''         # ssh port
DEPLOY_DIR=''          # server directory to rsync files to

BACKUP_HOST=''         # hostname or IP for backup
BACKUP_USER=''         # ssh user
BACKUP_PORT=''         # ssh port
BACKUP_DIR=''          # server directory to rsync zip to
```
