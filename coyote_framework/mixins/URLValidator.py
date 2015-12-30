__author__ = 'justin'

import urllib2


def validate_url(url, allowed_response_codes=None):
    """Validates that the url can be opened and responds with an allowed response code; ignores javascript: urls

    url -- the string url to ping
    allowed_response_codes -- a list of response codes that the validator will ignore
    """
    allowed_response_codes = [200] if allowed_response_codes is None else allowed_response_codes

    # link calls a js function, do not try to open
    if str(url).startswith('javascript:'):
        return True

    try:
        response = urllib2.urlopen(urllib2.Request(url))
    except urllib2.URLError:
        raise AssertionError('Url was invalid and could not be opened: {url}'.format(url=url))

    if response.code not in allowed_response_codes:
        raise AssertionError('Invalid response code {response_code} from url: {url}'
                             .format(response_code=response.code, url=url))
    return True


def validate_urls(urls, allowed_response_codes=None):
    """Validates that a list of urls can be opened and each responds with an allowed response code

    urls -- the list of urls to ping
    allowed_response_codes -- a list of response codes that the validator will ignore
    """

    for url in urls:
        validate_url(url, allowed_response_codes=allowed_response_codes)
    return True