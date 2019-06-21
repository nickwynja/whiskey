"""Markdown formatters"""

from whiskey import app
import markdown


def poetic_formatter(source, language, css_class, options, md):
    p = "<p class='mdx-peom--stanza'>"
    for line in source.splitlines():
        if line == "":
            p += '</p><p class="mdx-poem--stanza">'
        else:
            p += '<span class="mdx-poem--line">%s<br></span>' % line.strip()
    p += '</p>'
    html = markdown.markdown(
        '<blockquote class="%s" markdown="span">%s</blockquote>'
        % (css_class, p),
        extensions=app.config['MARKDOWN_EXTENSIONS']
    )
    return html
