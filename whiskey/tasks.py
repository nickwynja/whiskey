import os
import subprocess
import click
import datetime
import yaml
import shutil
import sys
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
        rsync_project(local_dir="%s/build/" % os.getcwd(),
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
    helpers.make_tarfile(build_tar, "%s/build" % os.getcwd())
    helpers.make_tarfile(content_tar, "./content")
    puts("...done")

    try:
        put(build_tar, app.config['BACKUP_DIR'])
        put(content_tar, app.config['BACKUP_DIR'])
    finally:
        disconnect_all()

    os.remove(build_tar)
    os.remove(content_tar)


@task
def freeze_to_build(skip_existing):
    app.config['PUBLISH_MODE'] = True
    app.config.update(FREEZER_SKIP_EXISTING=skip_existing)

    pages = [u for u in freezer.all_urls()]
    deduped_pages = []
    for i in pages:
        if i not in deduped_pages:
            deduped_pages.append(i)

    if sys.stdout.isatty():
        with click.progressbar(
                freezer.freeze_yield(),
                length=len(deduped_pages),
                show_pos=True,
                width=30,
                show_eta=False,
                show_percent=True,
                # item_show_func=lambda p: p.url if p else 'Done!'
        ) as urls:
            for url in urls:
                # everything is already happening, just pass
                pass
    else:
        print("Freezing site...")
        for g in freezer.freeze_yield():
            print("     Froze %s" % g.path)


@task
def generate_resume_pdf(output="%s/resume.pdf" % app.config['CONTENT_PATH']):
    try:
        print(
            ("\033[0;33m[whiskey]:\033[0;0m "
             "Generating resume pdf with pandoc\n"
             "           to %s...         " % output),
            end="", flush=True)

        filters = ""
        for f in app.config['PANDOC_FILTERS_RESUME']:
            filters += "--filter=%s" % f

        subprocess.check_output(
            ["pandoc",
             "-f", "markdown",
             "-t", "latex",
             filters,
             "--pdf-engine=lualatex",
             "--variable=subparagraph",
             "--template=%s/resume.tex" % app.config['TEMPLATE_PATH'],
             "--top-level-division=chapter",  # lets h2 to be heading
             "%s/resume.md" % app.config['CONTENT_PATH'],
             "-o", output
             ]
        )
        print("\033[0;32m DONE \033[0;0m")
    except subprocess.CalledProcessError as ex:
        print("\033[0;31m ERROR \033[0;0m")
        print("\nPandoc failed with error code", ex.returncode)
        sys.exit(ex.returncode)


@task
def add_update(text, featured):
    fname = "{}/{}".format(app.config['DATA_PATH'], "updates.yaml")
    d = datetime.datetime.now()
    u = [{"date": d.replace(microsecond=0),
          "featured": featured,
          "text": literal_unicode(text)}]

    with open(fname, "a") as f:
        yaml.dump(u, f, default_flow_style=False)


@task
def clean_assets():
    paths_to_clean = [
        'src/static/.webassets-cache',
        'src/static/gen',
    ]
    for path in paths_to_clean:
        if os.path.exists(path):
            shutil.rmtree(path)
