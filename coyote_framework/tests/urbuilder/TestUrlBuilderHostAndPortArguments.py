import unittest
from coyote_framework.util.urls.urlbuilder import UrlBuilder

__author__ = 'justin@shapeways.com'


class TestUrlBuilderHostAndPortArguments(unittest.TestCase):
    """Test cases for the Port an Host arguments and their permutations"""

    def setUp(self):
        super(TestUrlBuilderHostAndPortArguments, self).setUp()

        class data(object):
            url_no_port = 'http://urlnoport.com/'
            url_with_port = 'http://urlwithport.com:123/'

        self.data = data()

    def test_no_port_host(self):
        """Test that the full url supplied as the host will return the full url when no port is specified"""
        url = UrlBuilder.build(template='/', host=self.data.url_no_port)
        self.assertEqual(url, self.data.url_no_port)

    def test_port_in_host(self):
        """Test that the full url supplied as the host with a port will return the full url when no port is specified"""
        url = UrlBuilder.build(template='/', host=self.data.url_with_port)
        self.assertEqual(url, self.data.url_with_port)

    def test_no_port_in_host_and_port_override(self):
        """Test that the returned url will have the override port when a url with no port is specified"""
        port_override = 9000
        url = UrlBuilder.build(template='/', host=self.data.url_no_port, port=port_override)
        self.assertEqual(url, 'http://urlnoport.com:9000/')

    def test_port_in_host_and_port_override(self):
        """Test that the returned url will have the override port when a url with a different port is specified"""
        port_override = 8000
        url = UrlBuilder.build(template='/', host=self.data.url_with_port, port=port_override)
        self.assertEqual(url, 'http://urlwithport.com:8000/')
