#!/bin/bash

# trap signals to exit processes started by the script and
# terminate them when the script exits or fails
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

set -e

PYTHON=${PYTHON:-python3.10}

# Parse command line arguments.
NO_AI=0
DEPS_ONLY=0
VITE_OPTS=
UVICORN_HOST="localhost"
UVICORN_OPTS="$UVICORN_OPTS --port 5001"

while [[ $# -gt 0 ]]; do
	key="$1"
	case $key in
		--no-ai)
			NO_AI=1
			shift
			;;
		--deps-only)
			# Install dependencies and exit. Used by the Dockerfile to create a suitable image.
			DEPS_ONLY=1
			shift
			;;
		--host)
			VITE_OPTS="$VITE_OPTS --host"
			UVICORN_HOST="0.0.0.0"
			shift
			;;
		*)
		echo "Unknown argument: $key"
			exit 1
		;;
	esac
done

UVICORN_OPTS="$UVICORN_OPTS --host $UVICORN_HOST"

# Create a virtualenv, install dependencies, and run the dev server.
if [ ! -f .venv/bin/activate ]; then
	echo Creating a virtualenv and installing dependencies.
	$PYTHON -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt

	# Install AI requirements unless explicitly asked not to.
	if [ $NO_AI -eq 0 ]; then
		pip install -r rime/plugins/ai_requirements.txt
	fi
	echo Virtualenv created. To re-create this environment, delete .venv.
else

	source .venv/bin/activate

	# Check whether the currently installed packages are the same as
	# the ones specified in the requirements.txt file
	EXIT_STATUS=0
	$PYTHON check_dependencies.py || EXIT_STATUS=$?

	# Ask user whether to update the packages and proceed with installation when
	# the .venv installed packages do not match the ones in the requirements.txt
	if [ $EXIT_STATUS -eq 1 ]; then
		echo "There is a mismatch between the currently installed packages and requirements.txt"
		echo "Do you want to install the packages from requirements.txt with the specified versions? [y/n]"
		read -n 1 ANSWER

		if [[ $ANSWER == "y" ]]; then
			pip install -r requirements.txt
		fi
	fi
fi

cd frontend

# Always npm install because it doesn't take long.
npm install

# Exit if we only want to install dependencies.
if [ $DEPS_ONLY -eq 1 ]; then
	exit 0
fi

# Start Vite in the background. It will be killed when the script exits.
npm run dev -- $VITE_OPTS &
VITE_PID=$!

# Start Uvicorn in the foreground, running the backend.
uvicorn --reload --reload-dir ../rime --interface asgi3 $UVICORN_OPTS --factory rimeserver:create_app


npm run serve

