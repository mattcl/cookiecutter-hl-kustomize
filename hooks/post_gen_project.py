import os
import shutil
import subprocess

# if we're using a db, we're going to generate the sealed secret and remove the
# file that created the secret before potentially committing to the git repo
generate_db_secret = {% if cookiecutter.database != "none" %}True{% else %}False{% endif %}

if generate_db_secret:
    import base64

    print("> Generating DB passwords")
    # we want to replace the placeholders in the generated file with the encoded
    # generated secrets. We're just going to use the cookiecutter extension here
    # to generate the random strings
    db_password = base64.b64encode("{{ random_ascii_string(24, punctuation=False) }}".encode("utf-8"))
    db_postgres_password = base64.b64encode("{{ random_ascii_string(24, punctuation=False) }}".encode("utf-8"))

    with open("installs/default/raw-db-secret.yaml", "r") as file:
        contents = file.read()

    contents = contents.replace("REPLACE_POSTGRES_PASSWORD", str(db_password, "utf-8"))
    contents = contents.replace("REPLACE_POSTGRES_POSTGRES_PASSWORD", str(db_postgres_password, "utf-8"))

    # write the modified content back to the file
    with open("installs/default/raw-db-secret.yaml", "w") as file:
        file.write(contents)

    print("> Sealing generated secret")

    subprocess.call([
        "kubeseal",
        "--format",
        "yaml",
        "--scope",
        "namespace-wide",
        "-n",
        "{{ cookiecutter.namespace }}",
        "-f",
        "installs/default/raw-db-secret.yaml",
        "-w",
        "installs/default/db-secret.yaml"
    ])

# move the gitignore to .gitignore. We do this so it doesn't get treated as a
# .gitignore file by the template's repo
shutil.move("gitignore", ".gitignore")

# remove unneeded files
REMOVE_PATHS = [
    '{% if cookiecutter.ingress == "none" %}components/app/ingress.yaml{% endif %}',
    '{% if cookiecutter.database == "none" %}components/db{% endif %}',
    '{% if cookiecutter.redis == "no" %}components/redis{% endif %}',
    '{% if cookiecutter.database == "none" %}installs/default/raw-db-secret.yaml{% endif %}',
    '{% if cookiecutter.database == "none" %}installs/default/db-secret.yaml{% endif %}',
    '{% if cookiecutter.database == "none" %}installs/default/db-connect.env{% endif %}',
    '{% if cookiecutter.database == "none" %}installs/default/db-config.env{% endif %}',
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path and os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.unlink(path)


# Initialize git repository if requested
# the yes/no bool flags in the json are not in the stable release of
# cookiecutter that's on pypi
init_git = {% if cookiecutter.initialize_git_repo == "yes" %}True{% else %}False{% endif %}

if init_git:
    print("> Initializing git repository")
    subprocess.call(["git", "init"])
    subprocess.call(["git", "add", "*"])
    subprocess.call(["git", "commit", "-m", "Cookiectutter generated initial commit"])
else:
    print("> Skipping git init")
