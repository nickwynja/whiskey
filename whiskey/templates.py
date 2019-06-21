from whiskey import app, helpers
import jinja2


app.jinja_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader(app.config['TEMPLATE_PATH']),
    jinja2.FileSystemLoader('sites/_global/templates')
])

app.jinja_env.filters['datetime'] = helpers.format_date
app.jinja_env.filters['datetime_month_year'] = helpers.format_month_year
