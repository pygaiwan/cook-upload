from copy import deepcopy
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from .constants import OPENAI_MESSAGE
from .models import ExtractionResponse, ImageRequest


def parse_image(client: OpenAI, base64_image) -> tuple[str, str, str]:
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
        translation = str.maketrans('- :.@', '____')
        error_file = Path(f'error_{str(datetime.now()).translate(translation)}.json')
        error_file.write_text(response.model_dump_json(indent=4))
        raise ValueError(f'Something was wrong with the GPT response. See {error_file}')

    data = response.parsed
    return data.title, data.ingredients, data.steps
