# Check whether the currently installed packages are the ones specified
# in the `requirements.txt` file.
#
# Exit with code 1 if any of the three is true:
#   - At least one of the currently installed packages has a different
#       version than the one specified in `requirements.txt`.
#   - At least one of the packages in `requirements.txt` is not currently installed.
#   - There is at leas a packages installed that is not in the `requirements.txt`.
#

import sys
import pkg_resources
from typing import Dict

# Quick lookup of currently installed packages and their versions
current_packages: Dict[str, str] = {}

for dist in pkg_resources.working_set:
    current_packages[dist.project_name] = dist.version

def check_package(req: str) -> bool:
    " Does 'req' (requirements.txt line) match the currently installed packages? "
    # Get the package name and the version
    version = None  # shut linter up
    if req.startswith('-e'):
        # Editable. Just check package name without version.
        if 'egg=' in req:
            project_name = req.split('#egg=')[1]
            check_version = False
        else:
            project_name = req.split('/')[-1]
            check_version = False
    else:
        project_name, version = req.strip().split('==')
        check_version = True

    project_name = project_name.replace('_', '-')

    if project_name not in current_packages:
        return False

    if check_version and current_packages[project_name] != version:
        return False

    return True

with open('requirements.txt') as requirements:
    for req in requirements:
        if not check_package(req.strip()):
            print(f'Requirements do not match for {req}')
            sys.exit(1)
