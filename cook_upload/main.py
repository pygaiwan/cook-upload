from base64 import b64encode
from os import environ
from pathlib import Path

import typer
from openai_actions import OpenAIActions

app = typer.Typer()
chatgpt = OpenAIActions(environ.get('OPENAI_API_KEY'), environ.get('OPENAI_PROJECT_ID'))


@app.command()
def upload(image_path: str):
    image_path = Path(image_path)
    image = b64encode(image_path.read_bytes()).decode('utf-8')
    response = chatgpt.parse_image(base64_image=image)
    print(response)


if __name__ == '__main__':
    app()
