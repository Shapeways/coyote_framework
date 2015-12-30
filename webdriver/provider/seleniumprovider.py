import base64
import httplib
import json
from selenium import webdriver

HOST = 'saucelabs.com'
JOB_ENDPOINT_TEMPLATE = '/rest/v1/{username}/jobs/{job_id}'
COMMAND_EXECUTOR_TEMPLATE = 'http://{username}:{key}@ondemand.saucelabs.com:80/wd/hub'

class SauceConnection(object):

    def __init__(self, username, key):
        self.username = username
        self.key = key

# driver instantiation should be abstract, not saucelabs implementation
#    def new_browser(self, capabilities=None):
#        """Returns a new remote driver with saucelabs command command executor
#
#        capabilities -- dictionary with browser's desired capabilities
#        """
#        self.driver_capabilities = {} if capabilities is None else capabilities
#        self.command_executor = COMMAND_EXECUTOR_TEMPLATE.format(username=username, key=key)
#        remote_driver = webdriver.Remote(
#            desired_capabilities = self.driver_capabilities,
#            command_executor = self.command_executor
#        )
#        return remote_driver

    def set_job_details(self, job_id, passed=True, name=None):
        """Sets a SauceLabs job passed status

        job_id -- saucelabs id of the job session
        passed -- boolean value if the job has passed
        """
        details = {'passed': passed}

        if name is not None:
            details.update({'name': name})

        return self.put_job(job_id, details)

    def put_job(self, job_id, body):
        """Makes a PUT request to SauceLabs job; returns True if request was successful, False otherwise

        job_id -- saucelabs id of the job session
        body -- dictionary of body content to put
        """
        body = json.dumps(body)
        connection = httplib.HTTPConnection(HOST)
        connection.request('PUT', 
                           JOB_ENDPOINT_TEMPLATE.format(username=self.username, job_id=job_id),
                           body,
                           headers=self._get_basic_auth_header(self.username, self.key))
        result = connection.getresponse()
        return result.status == 200

    @staticmethod
    def _get_basic_auth_header(username, key):
        """Private method for building the basic auth headers

        username -- saucelabs username
        key -- saucelabs api key
        """
        base64string = base64.encodestring('%s:%s' % (username, key))[:-1]
        return {'Authorization': 'Basic {}'.format(base64string)}