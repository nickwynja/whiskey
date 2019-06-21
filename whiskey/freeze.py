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


@freezer.register_generator
def page_not_found():
    yield "/404.html"
