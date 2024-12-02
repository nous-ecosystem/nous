from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any
import os


class PromptManager:
    def __init__(self, templates_dir: str = "src/chat/templates"):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir), autoescape=select_autoescape()
        )

    def render_prompt(self, template_name: str, **kwargs) -> str:
        """Render a prompt template with the given variables."""
        template = self.env.get_template(f"{template_name}.j2")
        return template.render(**kwargs)

    def get_system_prompt(self, template_name: str = "default_system", **kwargs) -> str:
        """Get the system prompt using the specified template."""
        return self.render_prompt(template_name, **kwargs)
