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

with open('requirements.txt') as requirements:
    for req in requirements:
        # Get the package name and the version
        project_name, version = req.split('==')

        # If the package is not installed or there is a version miss-match
        # exit with code (1)
        if (project_name not in current_packages or current_packages[project_name] != version):
            sys.exit(1)

        # Remove the entry from the dict if it's satisfied
        del current_packages[project_name]

# There are more packages installed than the ones in the `requirements.txt`
if len(current_packages) != 0:
    sys.exit(1)
