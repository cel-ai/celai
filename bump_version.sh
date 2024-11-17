#!/bin/bash

# Set the default version bump type to 'patch'
VERSION_TYPE=${1:-patch}

# Check if the provided argument is valid
if [[ ! "$VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
  echo "Usage: $0 [patch|minor|major]"
  exit 1
fi

# Bump the version using the specified type
poetry version $VERSION_TYPE

# Get the new version
NEW_VERSION=$(poetry version -s)

# Commit and create a tag
git add pyproject.toml
git commit -m "Bump version to $NEW_VERSION"
git tag "v$NEW_VERSION"
git push origin --tags