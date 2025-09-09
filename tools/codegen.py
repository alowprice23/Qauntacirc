# tools/codegen.py
"""
Code generation utilities for QuantaCirc.

This module provides tools for scaffolding new agents, generating boilerplate code
from templates, and reducing manual setup for new components. It enhances
developer productivity by automating repetitive coding tasks.

Key Features:
- Template-based code generation (Jinja2).
- Scaffolding for new agents, including directory structure and base files.
- Boilerplate reduction for common components like CRUD handlers or API endpoints.
"""

import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

# Assuming a 'templates' directory at the root of the project
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')

class CodeGenerator:
    """
    Manages the generation of code from templates.
    """
    def __init__(self, template_dir: str = TEMPLATE_DIR):
        """
        Initializes the CodeGenerator with a template directory.

        Args:
            template_dir (str): Path to the directory containing Jinja2 templates.
        """
        if not os.path.exists(template_dir):
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renders a template with the given context.

        Args:
            template_name (str): The name of the template file.
            context (Dict[str, Any]): A dictionary of variables to pass to the template.

        Returns:
            str: The rendered code as a string.
        """
        template = self.env.get_template(template_name)
        return template.render(context)

    def write_to_file(self, filepath: str, content: str):
        """
        Writes the generated content to a file.

        Args:
            filepath (str): The path to the output file.
            content (str): The content to write.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Generated file: {filepath}")


def scaffold_agent(agent_name: str, output_dir: str):
    """
    Generates the basic file structure and boilerplate for a new agent.

    Args:
        agent_name (str): The name of the new agent (e.g., 'photon_detector').
        output_dir (str): The root directory where the agent's folder will be created.
    """
    generator = CodeGenerator()
    agent_dir = os.path.join(output_dir, agent_name)

    if os.path.exists(agent_dir):
        print(f"Agent directory already exists: {agent_dir}")
        return

    print(f"Scaffolding new agent '{agent_name}' in {output_dir}...")

    # Define context for the templates
    context = {
        'agent_name': agent_name,
        'agent_class_name': ''.join(word.capitalize() for word in agent_name.split('_')),
    }

    # Define files to be generated
    files_to_generate = {
        "agent.py.j2": os.path.join(agent_dir, "agent.py"),
        "ops.py.j2": os.path.join(agent_dir, "ops.py"),
        "prompts.py.j2": os.path.join(agent_dir, "prompts.py"),
        "__init__.py.j2": os.path.join(agent_dir, "__init__.py"),
    }

    for template, dest_path in files_to_generate.items():
        try:
            content = generator.render_template(template, context)
            generator.write_to_file(dest_path, content)
        except Exception as e:
            print(f"Error generating {dest_path}: {e}")
            # In a real scenario, we might need to clean up partially created files.

if __name__ == '__main__':
    # Example usage:
    # This would be typically called from a CLI command.
    print("Code Generation Tool")
    print("This is a library, not meant to be run directly for now.")
    # To test, one would need to create a `templates` directory with the
    # corresponding .j2 files.
    # e.g., scaffold_agent('example_agent', './agents')
