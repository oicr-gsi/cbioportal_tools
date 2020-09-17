
import logging
from utilities.base import base


class sample(base):

    """
    Sample for rShiny or cBioPortal reports. Input is a simple dictionary of attributes 
    (key/value pairs) for the sample. The only required attribute is SAMPLE_ID."""
    
    SAMPLE_ID_KEY = 'SAMPLE_ID'
    
    def __init__(self, attributes, log_level=logging.WARNING, log_path=None):
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__), log_path)
        self.sample_id = attributes.get(self.SAMPLE_ID_KEY)
        if self.sample_id == None:
            msg = "Missing required input key %s" % self.SAMPLE_ID_KEY
            self.logger.error(msg)
            raise ValueError(msg)
        self.attributes = attributes

    def get(self, key):
        return self.attributes.get(key)
        
    def get_attributes(self):
        return self.attributes

    def get_id(self):
        return self.sample_id
