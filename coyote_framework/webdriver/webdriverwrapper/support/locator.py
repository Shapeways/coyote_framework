__author__ = 'justin'


class Locator(object):

    ID = 'id'
    CSS = 'css'
    XPATH = 'xpath'
    CLASS_NAME = 'class_name'
    LINK_TEXT = 'link_text'
    PARTIAL_LINK_TEXT = 'partial_link_text'
    NAME = 'name'
    TAG_NAME = 'tag_name'
    TEXT = 'text'
    PARTIAL_TEXT = 'partial_text'

    def __init__(self, by, locator, description=None):
        """
            by -- the method used to select the locator
            locator -- the actual string used to locate the element
            description -- a description of what the locator is used for
        """
        self.by = by
        self.locator = locator
        self.description = description if description is not None else 'no description'

    def __repr__(self):
        return '''({by}, {locator}, {description})'''.format(
            by=self.by, locator=self.locator, description=self.description
        )

    def build(self, **variables):
        """Formats the locator with specified parameters"""
        return Locator(self.by, self.locator.format(**variables), self.description)