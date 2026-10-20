import logging
from ollama import generate
from winerecommender.models.attributes import WineQueryFilter

from src.winerecommender.configs.templates import WINE_QUERY_EXTRACTION_PROMPT, WINE_QUERY_EXTRACTION_INSTRUCTION

logger = logging.getLogger(__name__)

class ExtractorModel:
    def __init__(self, extractor_model: str):
        logger.info(f"Loading extractor model {extractor_model}")
        self.extractor_model = extractor_model
        logger.info(f"Initialised extractor model: {extractor_model}")
    
    def extract(self, query: str) -> WineQueryFilter:
        response = generate(
            model=self.extractor_model,
            system=WINE_QUERY_EXTRACTION_PROMPT,
            prompt=WINE_QUERY_EXTRACTION_INSTRUCTION.format(query=query),
            format=WineQueryFilter.model_json_schema()
        )
        if response.response is None:
            raise ValueError("Ollama returned an empty response object")
        return WineQueryFilter.model_validate_json(response.response)
