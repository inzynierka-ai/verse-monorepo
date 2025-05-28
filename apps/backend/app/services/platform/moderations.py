import logging
from enum import Enum
from typing import Optional, Dict

from openai import AsyncOpenAI
from openai.types import Moderation
from tenacity import retry, stop_after_attempt, wait_exponential

from langfuse.decorators import observe  # type: ignore


class ModerationModelName(str, Enum):
    """
    The name of the moderation model to use.
    """
    OMNI_MODERATION_LATEST = "omni-moderation-latest"
    # TEXT_MODERATION_LATEST was removed by user


class ModerationsService:
    """
    Service for moderating content using the OpenAI Moderations API.
    """

    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client
        self.logger = logging.getLogger(__name__)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    @observe(name="moderate_content")
    async def moderate_content(
        self,
        input_text: str,
        model: ModerationModelName = ModerationModelName.OMNI_MODERATION_LATEST,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Moderation:
        """
        Check content for potential harm using the OpenAI Moderations API.

        Args:
            input_text: Text to moderate.
            model: Moderation model to use.
            metadata: Additional metadata for the request.

        Returns:
            The full response object from the Moderations API.
        """
        trace_metadata = {
            "model": model.value,
            "input_text_length": len(input_text),
        }
        if metadata:
            trace_metadata.update(metadata)

        try:
            response = await self.openai_client.moderations.create(
                model=model.value,
                input=input_text,
            )

            return response.results[0]

        except Exception as api_error:
            error_str = str(api_error)
            self.logger.error("Moderation API error: %s", error_str)
            raise ValueError(f"Moderation API error: {error_str}") from api_error

    async def process_moderation(self, input_text: str) -> Dict[str, bool] | None:
        moderation_response = await self.moderate_content(input_text)
        is_flagged = self.is_flagged(moderation_response)
        if not is_flagged:
            return None
        violated_categories = self.get_violated_categories(moderation_response)

        return violated_categories

    def is_flagged(self, moderation_response: Moderation) -> bool:
        """Checks if the moderation response is flagged.

        Args:
            moderation_response: The response object from the moderate_content method.

        Returns:
            True if flagged, False otherwise.
        """
        return moderation_response.flagged

    def get_violated_categories(self, moderation_response: Moderation) -> Dict[str, bool]:
        """Gets a dictionary of categories that are marked as True (violated).

        Args:
            moderation_response: The response object from the moderate_content method.

        Returns:
            A dictionary with category names as keys and True as value if violated.
        """
        violated_categories: Dict[str, bool] = {}
        if moderation_response.categories:
            categories_dict = moderation_response.categories.model_dump()

            for category_name, is_violated in categories_dict.items():
                if is_violated:
                    violated_categories[category_name] = True
        return violated_categories
