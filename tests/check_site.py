"""Dependency-free checks for the homepage's structure and verified metadata."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.images = [], [], []
        self.headings, self.titles = [], []
        self.capture_title = False
        self.title = ''
        self.head = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs)
        if tag == 'img':
            self.images.append(attrs)
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self.headings.append(tag)
        if tag == 'h4':
            self.capture_title, self.title = True, ''

    def handle_data(self, data):
        if self.capture_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == 'h4':
            self.titles.append(self.title)
            self.capture_title = False


class HomepageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()
        cls.site = SiteParser()
        cls.site.feed(cls.html)

    def test_structure_and_navigation(self):
        self.assertEqual(self.site.lang, 'en')
        self.assertEqual(self.site.headings.count('h1'), 1)
        self.assertEqual(len(self.site.ids), len(set(self.site.ids)))
        for link in self.site.links:
            if link.get('href', '').startswith('#'):
                self.assertIn(link['href'][1:], self.site.ids)
            if link.get('target') == '_blank':
                self.assertIn('noopener', link.get('rel', ''))

    def test_vggt_equal_contribution(self):
        paper = self.html.split('id="vggt-bridge"')[1].split('</li>')[0]
        self.assertIn('Sungjae Choi<sup>*</sup>, <strong>Hanna Bae<sup>*</sup></strong>, Sunghyun Baek, and Junmo Kim', paper)
        self.assertEqual(paper.count('<sup>*</sup>'), 2)
        self.assertIn('* Equal contribution', paper)

    def test_independent_scroll_and_keywords(self):
        css = (ROOT / 'style.css').read_text()
        js = (ROOT / 'script.js').read_text()
        self.assertIn('tabindex="0"', self.html)
        self.assertIn("pane?.addEventListener('scroll'", js)
        self.assertIn('overscroll-behavior-y:contain', css)
        self.assertIn('@media(max-width:820px)', css)
        for keyword in ['3D Reconstruction', 'Multi-View Geometry', 'Visual SLAM', 'Sensor Fusion', 'Autonomous Driving']:
            self.assertIn('<li>' + keyword + '</li>', self.html)

    def test_strict_html_nesting(self):
        stack, errors = [], []
        void = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
        class NestingParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag not in void: stack.append(tag)
            def handle_endtag(self, tag):
                if tag in void: return
                if not stack or stack[-1] != tag: errors.append((tag, list(stack)))
                elif stack: stack.pop()
        NestingParser().feed(self.html)
        self.assertEqual(errors, [])
        self.assertEqual(stack, [])

    def test_education_before_publications(self):
        self.assertLess(self.html.index('<section id="education"'), self.html.index('<section id="publications"'))
        self.assertLess(self.html.index('href="#education"'), self.html.index('href="#publications"'))
        self.assertNotIn('Coursework:', self.html)
        self.assertNotIn('Laboratory, advised by Prof. Junmo Kim.', self.html)
        self.assertNotIn('I study geometric consistency in long-sequence 3D reconstruction.', self.html)

    def test_requested_layout(self):
        self.assertIn('<aside class="profile"', self.html)
        self.assertNotIn('id="teaching"', self.html)
        self.assertNotIn('href="#teaching"', self.html)
        self.assertIn('class="tags"', self.html)
        self.assertNotIn('class="keywords"', self.html)
        self.assertNotIn('class="pub-year"', self.html)
        bio = self.html.split('<div class="bio">')[1].split('</div>')[0]
        self.assertLess(len(bio.split()), 105)
        self.assertIn('particularly 3D reconstruction and robot vision.', bio)
        self.assertIn('from GIST, with minors in Mathematics and Artificial Intelligence.', bio)
        self.assertIn('https://scholar.google.com/citations?hl=ko&user=GdQtWNQAAAAJ', {link.get('href') for link in self.site.links})

    def test_profile_identity_and_avatar(self):
        self.assertIn('type="image/png" href="assets/ggyu-avatar.png?v=1"', self.html)
        self.assertIn('src="assets/profile.jpg"', self.html)
        self.assertIn('.profile > .portrait { align-self:center; }', (ROOT / 'style.css').read_text())
        self.assertIn('.profile .contact { justify-content:center; border-top:1px solid var(--panel-line);', (ROOT / 'style.css').read_text())
        self.assertIn('.profile .tags { justify-content:center; }', (ROOT / 'style.css').read_text())

    def test_images_and_local_assets(self):
        for image in self.site.images:
            self.assertTrue(image.get('alt'))
            self.assertTrue((ROOT / image['src']).is_file())
        for link in self.site.links:
            href = link.get('href', '')
            if href.startswith('assets/'):
                href = href.split('?')[0]
                self.assertTrue((ROOT / href).is_file())

    def test_accepted_work_is_first(self):
        self.assertEqual(len(self.site.titles), 6)
        self.assertEqual(self.site.titles[0], 'VGGT-Bridge: Beyond Sequential Pose Graphs via Coarse-Stride Skip Edges')
        self.assertEqual(self.site.titles[1], 'Analyzing the Effects of Table Preprocessing Methods on Korean Question-Answering Performance')
        self.assertLess(self.site.ids.index('table-qa'), self.site.ids.index('under-review'))
        self.assertLess(self.site.ids.index('under-review'), self.site.ids.index('info3r'))
        self.assertIn('ACCV 2026 · Accepted', self.html)

    def test_verified_metadata_and_links(self):
        urls = {link.get('href') for link in self.site.links}
        for url in ('https://arxiv.org/abs/2610.06594', 'https://arxiv.org/pdf/2610.06594',
                    'https://arxiv.org/abs/2609.21938', 'https://arxiv.org/pdf/2609.21938',
                    'https://doi.org/10.14329/isr.2025.27.2.071', 'https://github.com/BeCow5X5/VGGT-Bridge'):
            self.assertIn(url, urls)
        self.assertIn('Info3R: Information-Adaptive Test-Time Training for 3D Reconstruction', self.site.titles)
        self.assertIn('Sang-Huck Won, Jae-Hong Lee, Woo-Hyuk Jung, and Jihwan Woo', self.html)
        self.assertEqual(self.html.count(' · Under review'), 4)
        self.assertNotIn('Data Preprocessing Methods for Improving Korean Table Question Answering', self.html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
