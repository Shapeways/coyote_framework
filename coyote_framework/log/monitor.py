import logging
import time

from datadog import initialize, api

from coyote_framework.config.testrun_config import TestrunConfig


__author__ = 'justiniso'

REPORTING_HOST = 'rodb1.nyc.shapeways.net'
default_tags = ['aft']

# I die a little inside putting keys here
options = {
    'api_key': 'f4bcb7f45e7e13ca4734cc939d68768e',
    'app_key': '90f8da90ffc3563748d710419fd54946bab9b7a3'
}

initialize(**options)


def track_metric(metric, value, tags=None):
    """Track a metric in datadog (if config specifies to)

    :type metric: str
    :param metric: Metric to track, e.g. "aft.siteobjects.mockmodel.createtime"
    :param value: The value to push to datadog; should be numeric
    :type tags: list
    :param tags: Tags to push e.g. ["aft:siteobjects", "aft:browser"]
    :return: None
    """
    # Enforce naming pattern of "aft.xyz"
    if not metric.startswith('aft.'):
        metric = 'aft.{}'.format(metric)

    if TestrunConfig().get('datadog_track'):
        tags = tags or []
        tags += default_tags

        current_posix_time = time.time()
        response = api.Metric.send(
            metric=metric,
            points=(current_posix_time, value),
            host=REPORTING_HOST,
            tags=tags)

        if not response.get('status') == 'ok':
            logging.getLogger(__name__).critical('Datadog tracking failed: {}'.format(response))