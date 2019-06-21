from whiskey import app, tasks, flatpages, helpers
from fabric.tasks import execute
import click
import subprocess


@app.cli.command()
def drafts():
    """List files in post directory marked as draft"""
    drafts = [
        p for p in flatpages
        if p.path.startswith(app.config['POST_DIRECTORY'] if 'POST_DIRECTORY'
                             in app.config else '')
        and helpers.is_draft(p)
    ]
    for d in drafts:
        print('{}.md'.format(d.path))


@app.cli.command()
@click.confirmation_option(help='Do you want to build and publish?')
def publish():
    """Builds the site and deploys to server"""
    subprocess.run(["flask", "assets", "clean"])
    execute(tasks.freeze_to_build)
    execute(tasks.deploy_using_rsync)


@app.cli.command()
def build():
    """Builds the site and all files"""
    execute(tasks.freeze_to_build)


@app.cli.command()
def reload():
    """Runs a livereload server"""
    from livereload import Server
    server = Server(app.wsgi_app)
    server.watch('sites/personal/content/resume.md', tasks.generate_resume_pdf)
    server.watch(app.config['CONTENT_PATH'])
    server.serve(host='0.0.0.0', port=5000, debug=True)


@app.cli.command()
def deploy():
    """Deploys site using rsync"""
    execute(tasks.deploy_using_rsync)


@app.cli.command()
def backup():
    """Backs up site to local server"""
    execute(tasks.backup_using_fabric)


@app.cli.command()
@click.option('-o', '--output',
              default="sites/personal/content/resume.pdf",
              type=str)
def resume(output):
    """Generates PDF of resume using pandoc"""
    execute(tasks.generate_resume_pdf, output)


@app.cli.command()
@click.option('-f', '--featured',
              is_flag=True,
              default=False)
@click.argument('text', required=True)
def update(text, featured):
    """Adds a status update from command line"""
    execute(tasks.add_update, text, featured)
