#!/usr/bin/env zsh

echo "Delete local tag"
git tag -d v1.0.0

echo "Delete remote tag"
git push origin :refs/tags/v1.0.0

echo "Create new local tag"
git tag v1.0.0

echo "Push tag to remote"
git push origin v1.0.0
