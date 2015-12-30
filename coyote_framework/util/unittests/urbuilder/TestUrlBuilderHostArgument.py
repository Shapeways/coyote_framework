import unittest
from coyote_framework.util.urls.urlbuilder import UrlBuilder

__author__ = 'justin@shapeways.com'


class TestUrlBuilderHostArgument(unittest.TestCase):

    def setUp(self):
        super(TestUrlBuilderHostArgument, self).setUp()
        self.host_full_url = 'http://fullurl.com'
        self.host_no_scheme = 'fullurl.com'
        self.no_host_relative_path = '/endpoint'

    def test_full_url(self):
        """Test that the full url supplied as the host will return the full url"""
        url = UrlBuilder.build(template='/', host=self.host_full_url)
        assert url == 'http://fullurl.com/', 'Full url was not built correctly: "{}"'.format(url)

    def test_url_no_scheme_expect_usage_error(self):
        """Test that the host (no slash, no scheme, no www) will throw an error"""
        error = None
        try:
            UrlBuilder.build(template='/', host=self.host_no_scheme, scheme=None)
        except ValueError, error:
            pass

        self.assertIsNotNone(error, 'There should be a usage error when specifying a host with no scheme')

    def test_relative_url(self):
        url = UrlBuilder.build(template=self.no_host_relative_path, host=None)
        self.assertEqual(self.no_host_relative_path, url)
