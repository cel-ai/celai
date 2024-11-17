#!/bin/bash


# 1. **Bump the Patch Version Without Publishing:**

#    If you want to bump the patch version but do not want to commit or tag the changes yet, you can run:
#    ```bash
#    ./bump_version.sh patch
#    ```
#    This will update the version in `pyproject.toml` but will not commit or tag the changes.

# 2. **Bump the Minor Version and Publish:**
#    To bump the minor version and also commit and tag the changes, use the `--publish` flag:
#    ```bash
#    ./bump_version.sh minor --publish
#    ```
#    This will update the version, commit the changes with a message, create a tag, and push the tag to the remote repository.

# 3. **Bump the Major Version Without Publishing:**
#    If you want to bump the major version but hold off on committing and tagging, you can run:
#    ```bash
#    ./bump_version.sh major
#    ```
#    This will only update the version in `pyproject.toml`.

# 4. **Bump the Major Version and Publish:**
#    To bump the major version and immediately commit and tag the changes, use:
#    ```bash
#    ./bump_version.sh major --publish
#    ```
#    This will perform all the actions: version bump, commit, tag creation, and pushing the tag.

# 5. **Invalid Usage:**
#    If you provide an invalid version type, the script will display a usage message:
#    ```bash
#    ./bump_version.sh invalid
#    ```
#    Output:
#    ```
#    Usage: ./bump_version.sh [patch|minor|major] [--publish]
#    ```







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