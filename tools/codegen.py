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

    def generate_project(self, template_config, project_path, context):
        """Generates a project from a template."""
        files_to_generate = template_config.get("files", {})
        for template_file, output_path in files_to_generate.items():
            content = self.render_template(template_file, context)
            self.write_to_file(project_path / output_path, content)


import argparse
from typing import Literal

def scaffold_component(
    component_type: Literal["agent", "cli_command"],
    component_name: str,
    output_dir_root: str,
):
    """
    Generates the basic file structure and boilerplate for a new component.

    Args:
        component_type (str): The type of component to scaffold (e.g., 'agent').
        component_name (str): The name of the new component (e.g., 'photon_detector').
        output_dir_root (str): The root directory for that component type (e.g., './agents').
    """
    generator = CodeGenerator()
    component_dir = os.path.join(output_dir_root, component_name)

    if os.path.exists(component_dir) and component_type == "agent":
        print(f"Component directory already exists: {component_dir}")
        return

    print(f"Scaffolding new {component_type} '{component_name}' in {output_dir_root}...")

    context = {
        'component_name': component_name,
        'component_class_name': ''.join(word.capitalize() for word in component_name.split('_')),
    }

    files_to_generate = {}
    if component_type == "agent":
        context['agent_name'] = component_name
        context['agent_class_name'] = context['component_class_name']
        files_to_generate = {
            "agent.py.j2": os.path.join(component_dir, "agent.py"),
            "ops.py.j2": os.path.join(component_dir, "ops.py"),
            "prompts.py.j2": os.path.join(component_dir, "prompts.py"),
            "__init__.py.j2": os.path.join(component_dir, "__init__.py"),
        }
    elif component_type == "cli_command":
        context['command_name'] = component_name
        files_to_generate = {
            "cli_command.py.j2": os.path.join(output_dir_root, f"{component_name}.py"),
        }
    else:
        print(f"Unknown component type: {component_type}")
        return

    for template, dest_path in files_to_generate.items():
        try:
            content = generator.render_template(template, context)
            generator.write_to_file(dest_path, content)
        except Exception as e:
            print(f"Error generating {dest_path}: {e}")

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

    def generate_project(self, template_config, project_path, context):
        """Generates a project from a template."""
        files_to_generate = template_config.get("files", {})
        for template_file, output_path in files_to_generate.items():
            content = self.render_template(template_file, context)
            self.write_to_file(project_path / output_path, content)


def scaffold_agent(agent_name: str, output_dir: str):
    """
    Generates the basic file structure and boilerplate for a new agent.
    This is now a wrapper around scaffold_component.
    """
    scaffold_component("agent", agent_name, output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="QuantaCirc Code Generation Tool")
    parser.add_argument("component_type", choices=["agent", "cli_command"], help="The type of component to scaffold.")
    parser.add_argument("component_name", help="The name of the component (e.g., 'my_agent' or 'status').")
    parser.add_argument("--output_dir", help="The output directory for the component.")

    args = parser.parse_args()

    output_dirs = {
        "agent": "agents",
        "cli_command": "cli/commands",
    }

    output_dir = args.output_dir or output_dirs.get(args.component_type)

    if not output_dir:
        print(f"No default output directory for component type '{args.component_type}'. Please specify with --output_dir.")
    else:
        scaffold_component(args.component_type, args.component_name, output_dir)
