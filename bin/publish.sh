#!/usr/bin/env bash

set -euxo pipefail

# Check git status
git fetch --all
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "master" ]; then
    echo "This script must be run only when the master branch is checked out, but the current branch is ${CURRENT_BRANCH}. Abort!"
    exit 1
fi

NUM_BEHIND=$(git log ..origin/master | wc -l | awk '{print $1}')
if [ "$NUM_BEHIND" == "0" ]; then
    echo ""
else
    echo "Your branch is NOT up to date with origin/master. Abort! Please fetch and rebase first."
    exit 1
fi

# Update version and publish via commitizen
cz bump "$@"
