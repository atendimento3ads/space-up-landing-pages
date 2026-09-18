"""Refresh local CSS/JS content versions and the CSP's inline-script hashes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit
import base64
import hashlib
import re

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / 'index.html', *sorted(ROOT.glob('*/index.html'))]

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.inline = False
        self.content = ''
        self.hashes = set()
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.inline = 'src' not in dict(attrs)
            self.content = ''
    def handle_data(self, data):
        if self.inline:
            self.content += data
    def handle_endtag(self, tag):
        if tag == 'script' and self.inline:
            self.hashes.add('sha256-' + base64.b64encode(hashlib.sha256(self.content.encode()).digest()).decode())
            self.inline = False

hashes = set()
for page in PAGES:
    source = page.read_text()
    def version(match):
        attribute, address = match.groups()
        url = urlsplit(address)
        if url.scheme or not url.path.endswith(('.css', '.js')):
            return match.group(0)
        asset = (page.parent / url.path).resolve()
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        return attribute + '="' + urlunsplit((url.scheme, url.netloc, url.path, 'v=' + digest, url.fragment)) + '"'
    source = re.sub(r'(href|src)="([^"]+)"', version, source)
    page.write_text(source)
    parser = Scripts()
    parser.feed(source)
    hashes.update(parser.hashes)
policy_file = ROOT / '.htaccess'
policy = re.sub(r"'sha256-[^']+'\s*", '', policy_file.read_text())
policy = policy.replace("script-src 'self' ", "script-src 'self' " + ' '.join("'" + value + "'" for value in sorted(hashes)) + ' ')
policy_file.write_text(policy)
print(f'Updated CSS/JS versions and {len(hashes)} inline CSP hashes on {len(PAGES)} pages.')
