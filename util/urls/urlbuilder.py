import urllib
import urlparse


__author__ = 'justin@shapeways.com'

FILE_SCHEME = 'file'


class UrlBuilder(object):

    @staticmethod
    def build(template='/', host=None, scheme=None, port=None, **template_vars):
        """Builds a url with a string template and template variables; relative path if host is None, abs otherwise:
            template format: "/staticendpoint/{dynamic_endpoint}?{params}"
        """
        # TODO: refactor to build_absolute and build_relative instead of handling based on params
        parsed_host = urlparse.urlparse(host if host is not None else '')
        host_has_scheme = bool(parsed_host.scheme)

        if host_has_scheme:
            host = parsed_host.netloc
            # Prioritize scheme parameter, but if not specified, use scheme implied from host
            scheme = parsed_host.scheme if scheme is None else scheme

        port = port or parsed_host.port  # Default to port override

        unparsed_path = urlparse.urlparse(template.format(**template_vars)).geturl()

        # If a host was specified, try to return a full url
        if host:
            if not scheme:
                raise ValueError('No scheme supplied and scheme could not be inferred from the host: {}'.format(host))
            if port:
                host_no_port = host.partition(':')[0]  # Extract the host with no port supplied
                host = '{host_no_port}:{port}'.format(host_no_port=host_no_port, port=port)
            constructed_url = '//' + host + unparsed_path
            url = urlparse.urlparse(constructed_url, scheme=scheme).geturl()
        else:
            url = unparsed_path

        # Remove trailing parameter characters
        url = url[:-1] if url[-1] == '?' else url
        url = url[:-1] if url[-1] == '&' else url
        return url


    @staticmethod
    def build_file_url(path):
        """Builds a local file url

        @param path: The path to find
        @return: Built local URL
        """
        return urlparse.urlparse(path, scheme=FILE_SCHEME).geturl()

    @staticmethod
    def encode_params(**params):
        if len(params.keys()) < 1:
            return ''
        return urllib.urlencode(params)