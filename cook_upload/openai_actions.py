from copy import deepcopy

from openai import OpenAI

from .constants import OPENAI_MESSAGE
from .logger import logger
from .models import ExtractionResponse, ImageRequest


def parse_image(client: OpenAI, base64_image: str) -> tuple[str, str, str]:
    """
    Parses an image using the OpenAI API to extract relevant information.

    Args:
        client (OpenAI): An instance of the OpenAI client to communicate with the OpenAI API.
        base64_image (str): The base64 encoded string of the image to be parsed.

    Returns:
        tuple[str, str, str]: tuple with the extracted title, ingredients, and steps from the image.

    Raises:
        ValueError: If the GPT response is invalid or a refusal occurs.
    """
    message = deepcopy(OPENAI_MESSAGE)
    message['content'][1]['image_url']['url'] = f'data:image/jpeg;base64,{base64_image}'
    message = ImageRequest.model_validate(message)
    response = client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        messages=[message],
        response_format=ExtractionResponse,
    )
    response = response.choices[0].message

    if not response.parsed or response.refusal:
        msg = f'Something went wrong with the GPT response. {response.model_dump_json(indent=4)}'
        logger.error(msg)
        raise ValueError(msg)

    data = response.parsed
    logger.debug(f'GPT responded with {data}')
    return data.title, data.ingredients, data.steps
