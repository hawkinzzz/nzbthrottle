import logging
import requests
import json
import sys
from helpers import stream_throttle_helpers as stream_helper

class NZB(object):
    def __init__(self):
        self._logger = logging.getLogger()
        try:
            with open("./config.json") as w:
                self._logger.debug("Loading NZB config.json")
                cfg = json.load(w)
                self._logger.debug("NZB Config loaded successfully" + str(cfg))
                self._url = cfg['nzbget']['url']
                self._username = cfg['nzbget']['username']
                self._password = cfg['nzbget']['password']
                self._speedIncrements = cfg['nzbget']['speeds']
        except Exception as e:
            self._logger.exception("Problem encountered when creating NZB object")
            sys.exit(1)
    def get_speedIncrements(self):
        return self._speedIncrements

    def throttle_streams(self,active_streams):
        currRate = 0
        if(active_streams != 0):
            currRate = stream_helper.find_nearest(self._speedIncrements,active_streams)
        throttleResponse = json.loads(self.run_method("rate",currRate))
        if (throttleResponse["result"] == True):
            return True
        return False

    def run_method(self,method,params=None):
        try:
            self._logger.debug("Requesting method: " + str(method) + " with params: " + str(params))
            r = requests.post(self._url + '/{username}:{password}/jsonrpc'.format(username=self._username,password=self._password),headers={'Content-type':'application/json'},json={"method":method,"params": params if not None else []})
            if(r.status_code == 200):
                self._logger.debug("Response from NZBGet: " + str(r.text))
                return r.text
            else:
                self._logger.error("Did not get expected response from NZB API: %s",r.text)
        except Exception as e:
            self._logger.exception("Issue encountered when attempting to request method run from NZBGet")