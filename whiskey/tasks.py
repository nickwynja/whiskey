import os
import subprocess
import click
import datetime
import yaml
from whiskey import app, freezer, helpers
from fabric.network import disconnect_all
from fabric.contrib.project import rsync_project
from fabric.api import hosts, task, put, puts


class literal_unicode(str):
    pass


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(literal_unicode, literal_unicode_representer)


@hosts('%s@%s:%s' % (app.config.get('DEPLOY_USER', None),
                     app.config.get('DEPLOY_HOST', None),
                     app.config.get('DEPLOY_PORT', None)))
@task
def deploy_using_rsync():
    try:
        rsync_project(local_dir="./sites/%s/build/" % app.config['SITE_NAME'],
                      remote_dir=app.config['DEPLOY_DIR'],
                      delete=True)
    finally:
        disconnect_all()


@hosts('%s@%s:%s' % (app.config.get('BACKUP_USER', None),
                     app.config.get('BACKUP_HOST', None),
                     app.config.get('BACKUP_PORT', None)))
@task
def backup_using_fabric():
    '''Backup build and content files'''
    puts("Compressing `build` and `content`")
    today = datetime.datetime.now().strftime('%Y_%m_%d')
    build_tar = "/tmp/%s_build.tar.gz" % today
    content_tar = "/tmp/%s_content.tar.gz" % today
    helpers.make_tarfile(build_tar, "./sites/%s/build/" %
                         app.config['SITE_NAME'])
    helpers.make_tarfile(content_tar, "./sites/%s/content/" %
                         app.config['SITE_NAME'])
    puts("...done")

    try:
        put(build_tar, app.config['BACKUP_DIR'])
        put(content_tar, app.config['BACKUP_DIR'])
    finally:
        disconnect_all()

    os.remove(build_tar)
    os.remove(content_tar)


@task
def freeze_to_build():
    app.config['PUBLISH_MODE'] = True
    with click.progressbar(
            freezer.freeze_yield(),
            item_show_func=lambda p: p.url if p else 'Done!') as urls:
        for url in urls:
            # everything is already happening, just pass
            pass


@task
def generate_resume_pdf(output):
    try:
        print(
            ("\033[0;33m[whiskey]:\033[0;0m "
             "Generating resume pdf with pandoc\n"
             "           to %s...         " % output),
            end="", flush=True)
        subprocess.check_output(
            ["pandoc",
             "-f", "markdown",
             "-t", "latex",
             "--pdf-engine=xelatex",
             "--variable=subparagraph",
             "--template=sites/personal/templates/resume.tex",
             "--top-level-division=chapter",  # lets h2 to be heading
             "sites/personal/content/resume.md",
             "-o", output
             ]
        )
        print("\033[0;32m DONE \033[0;0m")
    except subprocess.CalledProcessError as ex:
        print("\033[0;31m ERROR \033[0;0m")
        print("\nPandoc failed with error code", ex.returncode)


@task
def add_update(text, featured):
    fname = "{}/{}".format(app.config['CONTENT_PATH'], "updates.yaml")
    d = datetime.datetime.now()
    u = [{"date": d.replace(microsecond=0),
          "featured": featured,
          "text": literal_unicode(text)}]

    with open(fname, "a") as f:
        yaml.dump(u, f, default_flow_style=False)
