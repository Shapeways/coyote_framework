"""
Module used to execute javascript on a webdriver session
"""

__author__ = 'justin'

import os
from selenium.common.exceptions import WebDriverException

from coyote_framework.webdriver.webdriverwrapper.exceptions import WebDriverJavascriptException


class JavascriptExecutor(object):
    """
    Class used to execute javascript on a driver_wrapper instance
    """

    def __init__(self, driver_wrapper):
        self.driver_wrapper = driver_wrapper

    def execute_script(self, string, args=None):
        """
        Execute script passed in to function

        @type string:   str
        @value string:  Script to execute
        @type args:     dict
        @value args:    Dictionary representing command line args

        @rtype:         int
        @rtype:         response code
        """
        result = None

        try:
            result = self.driver_wrapper.driver.execute_script(string, args)
            return result
        except WebDriverException:
            if result is not None:
                message = 'Returned: ' + str(result)
            else:
                message = "No message. Check your Javascript source: {}".format(string)

        raise WebDriverJavascriptException.WebDriverJavascriptException(self.driver_wrapper, message)

    def execute_template(self, template_name, variables, args=None):
        """
        Execute script from a template

        @type template_name:    str
        @value template_name:   Script template to implement
        @type args:             dict
        @value args:            Dictionary representing command line args

        @rtype:                 bool
        @rtype:                 Success or failure
        """
        js_text = self.build_js_from_template(template_name, variables)
        try:
            self.execute_script(js_text, args)
        except WebDriverException:
            return False
        return True

    def execute_template_and_return_result(self, template_name, variables, args=None):
        """
        Execute script from a template and return result

        @type template_name:    str
        @value template_name:   Script template to implement
        @type variables:        dict
        @value variables:       Dictionary representing template construction args
        @type args:             dict
        @value args:            Dictionary representing command line args

        @rtype:                 int
        @rtype:                 exit code
        """
        js_text = self.build_js_from_template(template_name, variables)
        return self.execute_script(js_text, args)

    def build_js_from_template(self, template_file, variables):
        """
        Build a JS script from a template and args

        @type template_file:    str
        @param template_file:   Script template to implement; can be the name of a built-in script or full filepath to
                                a js file that contains the script. E.g. 'clickElementTemplate.js',
                                'clickElementTemplate', and '/path/to/custom/template/script.js' are all acceptable
        @type variables:        dict
        @param variables:       Dictionary representing template construction args

        @rtype:                 int
        @rtype:                 exit code
        """
        template_variable_character = '%'

        # raise an exception if user passed non-dictionary variables
        if not isinstance(variables, dict):
            raise TypeError('You must use a dictionary to populate variables in a javascript template')

        # This filename is not a full file, attempt to locate the file in built-in templates
        if not os.path.isfile(template_file):
            # append the .js extension if not included
            if '.js' not in template_file:
                template_file += '.js'

            # find the template and read the text into a string variable
            templates_dir = os.path.join(os.path.dirname(__file__), 'jsTemplates')
            template_full_path = os.path.join(templates_dir, template_file)
        # The filename specified should be the full path
        else:
            template_full_path = template_file

        # Ensure that the file exists
        if not os.path.isfile(template_full_path):
            raise ValueError('File "{}" was not found; you must specify the name of a built-in javascript template '
                             'or the full filepath of a custom template'.format(template_full_path))

        try:
            js_text = open(template_full_path).read()
        except IOError:
            raise IOError('The template was not found or did not have read permissions: {}'.format(template_full_path))

        # replace all variables that match the keys in 'variables' dict
        for key in variables.keys():
            # double escape single and double quotes after variable replacement
            if hasattr(variables[key], 'replace'):
                variables[key] = variables[key].replace("'", "\\'")
                variables[key] = variables[key].replace('"', '\\"')
            else: # variable is not a string
                variables[key] = str(variables[key])

            js_text = js_text.replace(template_variable_character + key, variables[key])

        return js_text