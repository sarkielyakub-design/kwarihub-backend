from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader


template_path = (
    Path(__file__)
    .parent
    / "templates"
)

env = Environment(
    loader=FileSystemLoader(
        template_path,
    )
)


def render(
    template: str,
    **context,
):
    return env.get_template(
        template,
    ).render(
        **context,
    )