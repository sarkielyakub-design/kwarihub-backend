from abc import ABC, abstractmethod

from .engine import GeneratorEngine


class BaseGenerator(ABC):

    def __init__(self):
        self.engine = GeneratorEngine()

    @abstractmethod
    def generate(self, name: str):
        """
        Generate resource.
        """
        pass

    def render(self, template: str, context: dict):

        return self.engine.render_template(
            template,
            context
        )

    def write(
        self,
        path: str,
        content: str,
        overwrite=False,
    ):

        self.engine.write_file(
            path,
            content,
            overwrite,
        )