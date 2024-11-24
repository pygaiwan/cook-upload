from base64 import b64encode
from pathlib import Path

import pytest
from openai import BaseModel, OpenAI

from cook_upload import ImageRequest, parse_image


class Message(BaseModel):
    content: str
    refusal: str


class Choice(BaseModel):
    finish_reason: str
    message: Message


class MockResponse(BaseModel):
    id: str
    choices: list[Choice]


class Test_OpenAIActions:
    def test_image_in_model(self):
        base64_image = b'abcd'
        data = {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'What is in this image?',
                },
                {
                    'type': 'image_url',
                    'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'},
                },
            ],
        }
        assert ImageRequest.model_validate(data)

    @pytest.mark.vcr
    def test_parse_image(self, openai):
        img = Path(__file__).parent / 'images' / 'image.jpg'
        base64_image = b64encode(img.read_bytes()).decode('utf-8')
        title, ingredients, steps = parse_image(openai, base64_image)
        assert isinstance(title, str)
        assert isinstance(ingredients, str)
        assert isinstance(steps, str)

    def test_parse_fails(self, openai: OpenAI, mocker):
        response = {
            'id': 'chatcmpl-AV2E6tqg9DTGaUj4mtq3I35H38rTT',
            'choices': [
                {
                    'finish_reason': 'stop',
                    'message': {
                        'content': '',
                        'refusal': 'Refused',
                        'role': 'assistant',
                        'parsed': {},
                    },
                },
            ],
            'created': 1731960090,
        }

        response = MockResponse.model_validate(response)
        mocker.patch.object(openai.beta.chat.completions, 'parse', return_value=response)

        with pytest.raises(ValueError):
            parse_image(openai, b'abc')
