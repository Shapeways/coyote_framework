"""
Leverages Coyote URL builder
"""
from coyote_framework.util.urls.urlbuilder import UrlBuilder
from example.example_app.config.example_config import ExampleConfig

__author__ = 'matt'


class ExampleUrlBuilder(UrlBuilder):
    """Class for generating urls"""

    @staticmethod
    def build_follow_url(host=None, **params):
        """
        Build a URL for the /follow page
        """

        # template = '?{params}'
        config = ExampleConfig()
        template = '/follow?{params}'

        if not host:
            host = config.get('example_web_hostname')

        return ExampleUrlBuilder.build(
            template=template,
            host=host,
            params=ExampleUrlBuilder.encode_params(**params)
        )
