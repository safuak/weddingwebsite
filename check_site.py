import sys
import html.parser
from pathlib import Path
root = Path('engagement-site')
files = ['index.html','script.js','style.css']
missing = [p for p in files if not (root/p).exists()]
if missing:
    print('MISSING', missing)
    sys.exit(1)
print('FILES OK')
class P(html.parser.HTMLParser):
    def error(self, message):
        raise Exception(message)
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        pass
with open(root/'index.html', encoding='utf-8') as f:
    P().feed(f.read())
print('HTML parse OK')
