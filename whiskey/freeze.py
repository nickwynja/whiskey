from whiskey import app, freezer, helpers


@freezer.register_generator
def nested_content():
    files = helpers.list_files_in_dir(app.config['CONTENT_PATH'])
    if files:
        for file in files:
            yield file


@freezer.register_generator
def page():
    files = helpers.list_files_in_dir(app.config['CONTENT_PATH'], True)
    if files:
        for file in files:
            yield file

        ## also build resume pdf
        yield {'name': 'resume', 'dir': '', 'ext': 'pdf'}


@freezer.register_generator
def page_not_found():
    yield "/404.html"


@freezer.register_generator
def page_forbidden():
    yield "/403.html"
