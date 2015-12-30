from urlparse import urlparse
from selenium.common.exceptions import WebDriverException

__author__ = 'justin'


def is_subdomain(domain, reference):
    """Tests if a hostname is a subdomain of a reference hostname
    e.g. www.domain.com is subdomain of reference

    @param domain: Domain to test if it is a subdomain
    @param reference: Reference "parent" domain
    """
    index_of_reference = domain.find(reference)
    if index_of_reference > 0 and domain[index_of_reference:] == reference:
        return True
    return False



def dump_requestdriver_cookies_into_webdriver(requestdriver, webdriverwrapper, handle_sub_domain=True):
    """Adds all cookies in the RequestDriver session to Webdriver

    @type requestdriver: RequestDriver
    @param requestdriver: RequestDriver with cookies
    @type webdriverwrapper: WebDriverWrapper
    @param webdriverwrapper: WebDriverWrapper to receive cookies
    @param handle_sub_domain: If True, will check driver url and change cookies with subdomains of that domain to match
    the current driver domain in order to avoid cross-domain cookie errors
    @rtype: None
    @return: None
    """
    driver_hostname = urlparse(webdriverwrapper.current_url()).netloc

    for cookie in requestdriver.session.cookies:

        # Check if there will be a cross-domain violation and handle if necessary
        cookiedomain = cookie.domain
        if handle_sub_domain:
            if is_subdomain(cookiedomain, driver_hostname):
                # Cookies of requestdriver are subdomain cookies of webdriver; make them the base domain
                cookiedomain = driver_hostname

        try:
            webdriverwrapper.add_cookie({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookiedomain,
                'path': cookie.path
            })
        except WebDriverException, e:
            raise WebDriverException(
                msg='Cannot set cookie "{name}" with domain "{domain}" on url "{url}" {override}: {message}'.format(
                    name=cookie.name,
                    domain=cookiedomain,
                    url=webdriverwrapper.current_url(),
                    override='(Note that subdomain override is set!)' if handle_sub_domain else '',
                    message=e.message),
                screen=e.screen,
                stacktrace=e.stacktrace
            )


def dump_webdriver_cookies_into_requestdriver(requestdriver, webdriverwrapper):
    """Adds all cookies in the Webdriver session to requestdriver

    @type requestdriver: RequestDriver
    @param requestdriver: RequestDriver with cookies
    @type webdriver: WebDriverWrapper
    @param webdriver: WebDriverWrapper to receive cookies
    @rtype: None
    @return: None
    """

    for cookie in webdriverwrapper.get_cookies():
        # Wedbriver uses "expiry"; requests uses "expires", adjust for this
        expires = cookie.pop('expiry', {'expiry': None})
        cookie.update({'expires': expires})

        requestdriver.session.cookies.set(**cookie)