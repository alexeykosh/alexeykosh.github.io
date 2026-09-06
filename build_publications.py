import csv
import html
import re
from pathlib import Path


ROOT = Path(__file__).parent
CSV_FILE = ROOT / 'publications.csv'
HTML_FILE = ROOT / 'publications.html'
START = '<!-- PUBLICATIONS:START -->'
END = '<!-- PUBLICATIONS:END -->'
AUTHOR_NAME = 'Alexey Koshevoy'


def period(value):
    value = value.strip()
    return value if not value or value[-1] in '.!?' else f'{value}.'


def label_class(value):
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', value.lower()))


def authors_html(value):
    value = html.escape(period(value))
    return value.replace(AUTHOR_NAME, f'<strong>{AUTHOR_NAME}</strong>')


def publication_html(row):
    title = html.escape(row['title'].strip())
    label = row['label'].strip()
    authors = row['authors'].strip()
    details = row['details'].strip()
    links = ' '.join(
        f'<a href="{html.escape(row[key].strip(), quote=True)}">[{name}]</a>'
        for name, key in [('PDF', 'pdf'), ('Data', 'data'), ('Code', 'code')]
        if row[key].strip()
    )
    author_label = 'Authors' if re.search(r',|\band\b', authors, re.I) else 'Author'
    return f'''        <div class="publication">
            <h2>{title}<span class="publication-label publication-label-{label_class(label)}">{html.escape(label)}</span></h2>
            <p><strong>{author_label}:</strong> {authors_html(authors)}</p>
            <p><strong>Details:</strong> {html.escape(period(details))}</p>
            {f'<p>{links}</p>' if links else ''}
        </div>'''


def render():
    with CSV_FILE.open(newline='', encoding='utf-8') as source:
        publications = list(csv.DictReader(source, delimiter=';'))
    cards = '\n'.join(publication_html(row) for row in publications)
    page = HTML_FILE.read_text(encoding='utf-8')
    start = page.index(START) + len(START)
    end = page.index(END, start)
    page = f'{page[:start]}\n                <div class="content" id="publications-list">\n{cards}\n                </div>\n                {page[end:]}'
    HTML_FILE.write_text(page, encoding='utf-8')


if __name__ == '__main__':
    render()
    assert '<strong>Alexey Koshevoy</strong>' in HTML_FILE.read_text(encoding='utf-8')
    assert '[Data]' in HTML_FILE.read_text(encoding='utf-8')
