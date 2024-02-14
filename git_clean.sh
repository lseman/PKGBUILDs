#!/bin/bash

# Define the directory to search in
directory=$(pwd)
echo "Directory: $directory"
# Find all .git folders except in the main folder and delete them
find "$directory" -type d -name .git -not -path "$directory/.git" -exec rm -rf {} +
