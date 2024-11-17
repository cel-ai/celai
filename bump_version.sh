#!/bin/bash

# Set the default version bump type to 'patch'
VERSION_TYPE=${1:-patch}

# Check if the provided argument is valid
if [[ ! "$VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
  echo "Usage: $0 [patch|minor|major] [--publish]"
  exit 1
fi

# Bump the version using the specified type
poetry version $VERSION_TYPE

# Get the new version
NEW_VERSION=$(poetry version -s)

# Check if the --publish flag is present
PUBLISH=false
for arg in "$@"; do
  if [[ "$arg" == "--publish" ]]; then
    PUBLISH=true
    break
  fi
done

# Commit and create a tag if --publish is present
if $PUBLISH; then
  git add pyproject.toml
  git commit -m "Bump version to $NEW_VERSION"
  git tag "v$NEW_VERSION"
  git push origin --tags
else
  echo "Version bumped to $NEW_VERSION, but not committed or tagged. Use --publish to commit and tag."
fi