from abc import ABC,abstractmethod
import logging

import requests

logger = logging.getLogger(__name__)

class BaseNotifier(ABC):

    @abstractmethod
    def send_alert(self,message, metadata = None):
        pass
    
class HttpNotifier(BaseNotifier):
    def __init__(self, endpointurl, headers = None):
        self.endpointurl = endpointurl
        self.headers = headers or {'content-type': 'application/json'}

    def send_alert(self, message, metadata=None):
        payload = {
            'message':message,
            'metadata': metadata or {}         
        }

        response = requests.post(self.endpointurl,json=payload, headers=self.headers, timeout=5)

        if not response.ok:
            print(response.status_code)
            print(response.text)
            raise Exception("failed Http request")
        return response.json()


