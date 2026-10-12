"""Information on dependencies modules including:
* Dependencies based on current OS
* Modules that need to be explicitly included in standalone builds"""

import os

from personal_compile_tools.requirements import Requirement, parse_requirements_file

module_dependencies: list[Requirement] = parse_requirements_file("requirements.txt")

# Some modules can't be followed normally or need to
# be checked explicitly
modules_to_include: list[str] = [
    "image_viewer.image._read",
    "image_viewer._config",
]
if os.name == "nt":
    modules_to_include.append("image_viewer.utils._os_nt")


def get_normalized_module_name(module: Requirement) -> str:
    """Given the name used for pip install,
    return the name used to import the module in python."""
    module_name: str = module.name.lower()

    return {"pillow": "PIL"}.get(module_name, module_name)
