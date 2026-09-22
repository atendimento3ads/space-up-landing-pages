"""Check deployment URLs, local assets, structured FAQs, sitemap and CSP hashes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, parse_qs, unquote
import base64
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://services.spaceupconstruction.com/'
VERIFICATION_FILE = '7g70voolv25xx4zh31wo93uk6a16y0.html'
VERIFICATION_TOKEN = b'7g70voolv25xx4zh31wo93uk6a16y0'
PAGES = [ROOT / 'index.html', *sorted(ROOT.glob('*/index.html'))]
POLICY = (ROOT / '.htaccess').read_text()

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.elements = []
        self.scripts = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == 'script':
            self.current = [attrs, '']
    def handle_data(self, data):
        if self.current is not None:
            self.current[1] += data
    def handle_endtag(self, tag):
        if tag == 'script' and self.current is not None:
            self.scripts.append(self.current)
            self.current = None

canonicals = set()
count = 0
for page in PAGES:
    source = page.read_text()
    document = Document()
    document.feed(source)
    ids = {a['id'] for t, a in document.elements if 'id' in a}
    canon = [a['href'] for t, a in document.elements if t == 'link' and a.get('rel') == 'canonical']
    expected = BASE + (page.parent.name + '/' if page.parent != ROOT else '')
    assert canon == [expected], f'{page}: incorrect canonical URL'
    canonicals.add(expected)
    assert sum(t == 'h1' for t, a in document.elements) == 1, f'{page}: expected one H1'
    assert sum(t == 'meta' and a.get('name') == 'description' for t, a in document.elements) == 1
    assert 'href="https://3ads.com.br/">3ADS</a>' in source
    for stylesheet in [ROOT / 'styles.css', ROOT / 'assets/site.css', ROOT / 'siding-finishing/styles.css']:
        assert not re.search(r'@media\s*\([^)]*max-width:', stylesheet.read_text()), f'{stylesheet}: use mobile-first min-width enhancements'
    for tag, attrs in document.elements:
        refs = [attrs[k] for k in ('href', 'src', 'action') if k in attrs]
        refs += [item.strip().split()[0] for item in attrs.get('srcset', '').split(',') if item.strip()]
        if attrs.get('property') in ('og:image', 'og:url') or attrs.get('name') == 'twitter:image':
            refs.append(attrs['content'])
        for address in refs:
            url = urlsplit(address)
            if url.scheme and not address.startswith(BASE):
                continue
            if address.startswith(BASE):
                target = ROOT / unquote(url.path.lstrip('/'))
            elif url.path.startswith('/'):
                target = ROOT / unquote(url.path.lstrip('/'))
            elif not url.path:
                target = page
            else:
                target = page.parent / unquote(url.path)
            if target.is_dir():
                target = target / 'index.html'
            assert target.is_file(), f'{page}: missing {address}'
            if url.fragment:
                target_ids = ids if target == page else set(re.findall(r'id="([^"]+)"', target.read_text()))
                assert unquote(url.fragment) in target_ids, f'{page}: missing anchor {address}'
            if url.path.endswith(('.css', '.js')) and not url.scheme:
                expected_version = hashlib.sha256(target.read_bytes()).hexdigest()[:12]
                assert parse_qs(url.query).get('v') == [expected_version], f'{page}: stale version for {address}'
            count += 1
    for attrs, script in document.scripts:
        if 'src' in attrs:
            continue
        digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        assert "'sha256-" + digest + "'" in POLICY, f'{page}: unauthorized inline script'
        if attrs.get('type') == 'application/ld+json':
            graph = json.loads(script)['@graph']
            faq = next((node for node in graph if node['@type'] == 'FAQPage'), None)
            if faq:
                def plain(text):
                    from html import unescape
                    return unescape(re.sub('<[^>]+>', '', text)).strip()
                actual = [(plain(q), plain(a)) for q, a in re.findall(r'<details[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', source, re.S)]
                structured = [(q['name'], q['acceptedAnswer']['text']) for q in faq['mainEntity']]
                assert actual == structured, f'{page}: FAQ schema does not match visible answers'
    assert 'GTM-52FS343L' in document.scripts[0][1], f'{page}: GTM must be the first script'
    quote_forms = [a for t, a in document.elements if t == 'form' and 'quote-form' in a.get('class', '').split()]
    if page.parent.name in ('epoxy-flooring', 'siding-finishing'):
        assert len(quote_forms) == 1, f'{page}: expected one quote form'
        form = quote_forms[0]
        assert form.get('action') == '/submit-quote.php' and form.get('method') == 'post', f'{page}: incorrect form endpoint'
        assert 'data-quote-form' in form, f'{page}: JavaScript form enhancement missing'
        assert 'name="company_website"' in source, f'{page}: spam trap missing'
        assert 'name="submission_id"' in source, f'{page}: duplicate-submission protection missing'

urls = {node.text for node in ET.parse(ROOT / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
assert urls == canonicals, 'Sitemap must match all canonical URLs'
assert BASE + 'sitemap.xml' in (ROOT / 'robots.txt').read_text()
assert (ROOT / 'llm.txt').read_text() == (ROOT / 'llms.txt').read_text()
assert (ROOT / VERIFICATION_FILE).read_bytes() == VERIFICATION_TOKEN, 'Domain verification token changed'
assert "'unsafe-inline'" not in POLICY and "'unsafe-eval'" not in POLICY
for asset in ('assets', 'robots.txt', 'sitemap.xml', 'llm.txt', 'llms.txt', 'favicon.ico', 'submit-quote.php', VERIFICATION_FILE):
    assert asset in (ROOT / '.cpanel.yml').read_text(), f'Deployment recipe missing {asset}'
print(f'PASS: {len(PAGES)} pages, {count} local URLs/assets, sitemap, factual FAQ schema, asset versions and CSP hashes.')
