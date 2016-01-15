"""
Wrapper for python's "requests" library that has options to maintain session
and keep a history of responses in a queue
"""

import requests
from collections import deque


class RequestDriver(object):

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

    session = None
    responses = deque([])
    max_response_history = 100

    def __init__(self, persist_session_between_requests=True, max_response_history=None, verify_certificates=False):
        self.persist_session_between_requests = persist_session_between_requests
        self.verify_certificates = verify_certificates
        if max_response_history is not None:
            if not max_response_history >= 0:
                raise ValueError('You must specify a positive integer as a max number of past requests to store')

        if self.persist_session_between_requests:
            self.session = requests.Session()
        else:
            self.session = requests

    def request(self, uri, method=GET, headers=None, cookies=None, params=None, data=None, post_files=None):
        """Makes a request

        @param uri: The uri to send request
        @param method: Method to use to send request
        @param headers: Any headers to send with request
        @param cookies: Request cookies (in addition to session cookies)
        @param params: Request parameters
        @param data: Request data
        @rtype: requests.Response
        @return: The response
        """

        kwargs = {
            'headers': headers,
            'cookies': cookies,
            'params': params,
            'files': post_files,
            'data': data,
            'verify': self.verify_certificates,

        }

        if method == self.POST:
            response = self.session.post(uri, **kwargs)

        elif method == self.PUT:
            response = self.session.put(uri, **kwargs)

        elif method == self.DELETE:
            response = self.session.delete(uri, **kwargs)

        else:  # Default to GET
            response = self.session.get(uri, **kwargs)

        self.responses.append(response)

        while len(self.responses) > self.max_response_history:
            self.responses.popleft()

        return response

    def get_last_response(self):
        """Convenience method for retrieving the last response"""
        try:
            return self.responses[-1]
        except IndexError:
            return None

    def wipe_session(self):
        """Sets the driver's session to a new request session

        @return: None
        """
        self.session = requests.Session()

    def save_last_response_to_file(self, filename):
        """Saves the body of the last response to a file

        @param filename: Filename to save to
        @return: Returns False if there is an OS error, True if successful
        """
        response = self.get_last_response()
        return self.save_response_to_file(response, filename)

    def save_response_to_file(self, response, filename):
        """Saves the body of the last response to a file

        @param filename: Filename to save to
        @return: Returns False if there is an OS error, True if successful
        """
        try:
            last_response = self.get_last_response()
            with open(filename, 'w') as f:
                f.write(last_response.content)
        except OSError, e:
            return False
        return True