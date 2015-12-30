import urlparse
from coyote_framework.log import Logger

__author__ = 'justin@shapeways.com'


class WebPage(object):

    def __init__(self, driver=None, driver_wrapper=None, logger=None):
        """
        @type driver_wrapper: WebDriverWrapper
        @param driver_wrapper: Driver Wrapper
        """
        self.logger = logger if logger is not None else Logger.get()

        if driver is not None:
            self.driver = driver
            self.title = self.driver.title
            self.current_url = self.driver.current_url
            self.page_source = self.driver.page_source
        elif driver_wrapper is not None:
            self.driver_wrapper = driver_wrapper
            self.dw = self.driver_wrapper
            self.title = self.driver_wrapper.title()
            self.current_url = self.driver_wrapper.current_url()
            self.page_source = self.driver_wrapper.page_source()

    def get_page_hierarchy(self):
        return get_class_hierarchy(self)

    def is_page_loaded(self):
        """A method to include on pages to test if the page is loaded (likely by searching for a particular element; if
        not

        @raise: NotImplementedError
        """
        raise NotImplementedError(
            'This method has not been implemented for this page. You must implement this method to test if the page '
            'is loaded (e.g. by looking for an element unique to this page)'
        )

    def validate(self):
        pass


class WebComponent(object):
    """An object used to represent a partial component of a web page, e.g. a registration form, a footer, etc."""

    def __init__(self, element=None, parent_page=None, driver_wrapper=None, dependencies=None):
        """
        @param element: The component's container element, e.g. the "form" element of a registration form
        @type element: WebElementWrapper
        """
        self.parent_page = parent_page
        self.element = element
        self.driver_wrapper = driver_wrapper if driver_wrapper else element.driver_wrapper

        if dependencies is not None:
            for dependency in dependencies:
                if isinstance(dependency, DormantWebComponent):
                    raise ValueError("Cannot instantiate a {this} instance w/o first instantiating "
                                     "{dep} instance", this=self.__class__, dep=dependency.__class__)

        if element is None:
            raise ValueError('WebComponents must have a container element')

    def get_component_hierarchy(self):
        hierarchy = get_class_hierarchy(self)

        if self.parent_page:
            if isinstance(self.parent_page, WebPage):
                hierarchy += self.parent_page.get_page_hierarchy()
            else:
                hierarchy += self.parent_page.get_component_hierarchy()

        return hierarchy


class DormantWebComponent(object):
    """A placeholder class for WebComponents before they are initialized that will raise an exception if attributes are
    called.

    """
    def __getattribute__(self, item):
        """
        @raise: NotImplementedError
        """
        raise NotImplementedError(
            'This web component has not been initialized yet. Web components are not initialized'
            ' automatically for improved performance and scoped testing. You must explicitly'
            ' initialize web components before using them.'
        )


class WebPageRequests(object):
    """

    """
    def __init__(self, request_driver, host=None, scheme='http'):
        """
        @type request_driver: RequestDriver
        """
        self.host = host
        self.scheme = scheme
        self.rd = request_driver

    def get_base_url(self, scheme_override=None):
        if scheme_override is not None:
            scheme_tmp = scheme_override
        else:
            scheme_tmp = self.scheme

        url = urlparse.urlparse(self.host, scheme=scheme_tmp)
        url = url.geturl()
        return url


def get_class_hierarchy(_class):
    types = type(_class).mro()
    classes = [types[i].__name__ for i in xrange(0, len(types) - 1)]
    return classes