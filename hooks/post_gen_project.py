import os

# remove unneeded files
REMOVE_PATHS = [
    '{% if cookiecutter.ingress == "none" %}components/app/ingress.yaml{% endif %}',
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path and os.path.exists(path):
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.unlink(path)

# Initialize git repository if requested
# the yes/no bool flags in the json are not in the stable release of
# cookiecutter that's on pypi
init_git = {% if cookiecutter.initialize_git_repo == "yes" %}True{% else %}False{% endif %}

if init_git:
    print("> Initializing git repository")
    import subprocess
    subprocess.call(["git", "init"])
    subprocess.call(["git", "add", "*"])
    subprocess.call(["git", "commit", "-m", "Cookiectutter generated initial commit"])
else:
    print("> Skipping git init")
