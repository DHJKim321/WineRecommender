import logging

from winerecommender.adapters.extractor_model import ExtractorModel

logger = logging.getLogger(__name__)


class ExtractorService:
    
    def __init__(self, extractor_model: ExtractorModel):
        self.extractor_model = extractor_model

    def extract(self, query):
        try:
            return self.extractor_model.extract(query)
        except Exception:
            logger.exception("Structured extraction encountered an error")
            raise
