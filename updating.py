import os
import subprocess
import sys
import re
import shutil
def extract_variables(lines):
    variables = {}
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            variables[key.strip()] = value.strip().strip('"').strip("'")
    return variables

def replace_variables(string, variables):
    for key, value in variables.items():
        string = string.replace("${" + key + "}", value)
    return string

def extract_git_url(line, variables):
    line = replace_variables(line, variables)
    match = re.search(r'git\+([^\s"]+)', line)
    if match:
        return match.group(1)
    return None

def check_git_updates(git_url, branch="main"):
    temp_dir = "/tmp/git-checkout"
    # create a temporary directory
    os.makedirs(temp_dir, exist_ok=True)
    try:
        # Initialize a git repository in the temporary directory
        subprocess.check_call(['git', 'init'], cwd=temp_dir, stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

        # Add remote repository
        subprocess.check_call(['git', 'remote', 'add', 'origin', git_url], cwd=temp_dir, stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

        # Fetch all branches
        subprocess.check_call(['git', 'fetch', 'origin'], cwd=temp_dir, stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

        # Determine the default branch
        default_branch = subprocess.check_output(
            ['git', 'remote', 'show', 'origin'],
            cwd=temp_dir
        ).decode().split('\n')

        # Extract the default branch name
        for line in default_branch:
            if 'HEAD branch' in line:
                default_branch = line.split(':')[1].strip()
                break

        # Get the latest commit ID of the default branch
        commit_id = subprocess.check_output(
            ['git', 'rev-parse', f'origin/{default_branch}'],
            cwd=temp_dir
        ).decode().strip()

        return commit_id
    finally:
        # Clean up by removing the temporary directory
        shutil.rmtree(temp_dir)

def read_last_commit(directory):
    commit_file = os.path.join(directory, ".last_commit")
    if os.path.isfile(commit_file):
        with open(commit_file, "r") as file:
            return file.read().strip()
    return None

def write_last_commit(directory, commit):
    commit_file = os.path.join(directory, ".last_commit")
    with open(commit_file, "w") as file:
        file.write(commit)

def process_directory(directory):
    pkgbuild_path = os.path.join(directory, "PKGBUILD")
    if os.path.isfile(pkgbuild_path):
        with open(pkgbuild_path) as f:
            lines = f.readlines()

        variables = extract_variables(lines)
        last_commit = read_last_commit(directory)
        print(f"Last commit: {last_commit}")

        for line in lines:
            if "git+" in line:
                git_url = extract_git_url(line, variables)
                if git_url:
                    print(f"Checking updates for {git_url} in {directory}")
                    latest_commit = check_git_updates(git_url)
                    if (latest_commit and latest_commit != last_commit) or "--all" in sys.argv:
                        print(f"Latest commit: {latest_commit}")
                        print(f"Running makepkg in {directory}")
                        subprocess.run(["makepkg", "-sfiCc"], cwd=directory)
                        write_last_commit(directory, latest_commit)
                    else:
                        print(f"No updates found for {directory}")
                    break


def main(directories):
    for directory in directories:
        print("-" * 80)
        print(f"Processing {directory}")
        process_directory(directory)

if __name__ == "__main__":

    # create help for -h and --help
    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: python3 updating.py")
        print("--all: redo all packages")
        sys.exit(0)
    
    if "--repo" in sys.argv:
        root_folder = "/data/PKGBUILDS/"
        # run repo update
        # subprocess.run(["repo-add", "/data/PKGBUILDS/hyprland.db.tar.gz"] + [os.path.join(root_folder, pkg) for pkg in packages])
    
    if "--srcinfo" in sys.argv:
        # navigate to each folder root_folder and run makepkg makepkg --printsrcinfo > .SRCINFO

        # get all folders in root_folder
        root_folder = "/data/git/PKGBUILDs/"
        packages = os.listdir(root_folder)

        # get only dirs not files
        packages = [pkg for pkg in packages if os.path.isdir(os.path.join(root_folder, pkg))]

        for pkg in packages:
            # Run the command and capture the output
            result = subprocess.run(["makepkg", "--printsrcinfo"], cwd=os.path.join(root_folder, pkg), stdout=subprocess.PIPE, text=True)

            # Write the output to .SRCINFO
            with open(os.path.join(root_folder, pkg, ".SRCINFO"), "w") as file:
                file.write(result.stdout)

        sys.exit(0)

    root_folder = "/data/git/PKGBUILDs/"

    # Get list of packages from gitupdate.txt
    packages = []
    with open(root_folder + "gitupdate.txt", "r") as file:
        for line in file:
            packages.append(line.strip())    
    directories = [os.path.join(root_folder, pkg) for pkg in packages]
    main(directories)
