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

    def test_requested_layout(self):
        self.assertIn('<header class="profile" id="about"', self.html)
        self.assertNotIn('id="teaching"', self.html)
        self.assertNotIn('href="#teaching"', self.html)
        self.assertNotIn('class="tags"', self.html)
        self.assertNotIn('class="keywords"', self.html)
        self.assertNotIn('class="pub-year"', self.html)
        bio = self.html.split('<div class="bio">')[1].split('</div>')[0]
        self.assertLess(len(bio.split()), 55)

    def test_images_and_local_assets(self):
        for image in self.site.images:
            self.assertTrue(image.get('alt'))
            self.assertTrue((ROOT / image['src']).is_file())
        for link in self.site.links:
            href = link.get('href', '')
            if href.startswith('assets/'):
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
                    'https://doi.org/10.14329/isr.2025.27.2.071'):
            self.assertIn(url, urls)
        self.assertIn('Info3R: Information-Adaptive Test-Time Training for 3D Reconstruction', self.site.titles)
        self.assertIn('Sang-Huck Won, Jae-Hong Lee, Woo-Hyuk Jung, and Jihwan Woo', self.html)
        self.assertEqual(self.html.count(' · Under review'), 4)
        self.assertNotIn('Data Preprocessing Methods for Improving Korean Table Question Answering', self.html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
