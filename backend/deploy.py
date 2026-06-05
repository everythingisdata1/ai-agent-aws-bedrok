import shutil
import subprocess
from pathlib import Path

# Output package directory and zip file name
PACKAGE_DIR = Path("lambda-package")
ZIP_FILE = Path("lambda-package.zip")


def deploy():
    """
    Build an AWS Lambda deployment package.

    Steps:
    1. Remove any existing deployment artifacts.
    2. Install dependencies into a local package directory using the
       AWS Lambda Python 3.12 Docker image.
    3. Copy application source code and supporting files.
    4. Create a ZIP archive ready for Lambda deployment.
    """

    # Clean up previous build artifacts
    shutil.rmtree(PACKAGE_DIR, ignore_errors=True)
    ZIP_FILE.unlink(missing_ok=True)

    # Create a fresh package directory
    PACKAGE_DIR.mkdir()

    print("Installing dependencies for AWS Lambda...")

    # Install dependencies inside a Lambda-compatible environment
    result = subprocess.run(
        [
            "docker", "run", "--rm", "-v",
            f"{Path.cwd()}:/var/task",
            "--platform", "linux/amd64",
            "--entrypoint", "/bin/sh",
            "public.ecr.aws/lambda/python:3.12",
            "-c", (
            "pip install -r requirements.txt "
            "-t /var/task/lambda-package "
            "--platform manylinux2014_x86_64 "
            "--only-binary=:all: "
            "--no-cache-dir "
            "--upgrade"
        ),
        ],
        check=True,
    )

    result.check_returncode()
    # Copy application directories if they exist
    for folder in ("data", "src"):
        src = Path(folder)
        if src.exists():
            shutil.copytree(src, PACKAGE_DIR / folder)

    # Copy Lambda entry-point and supporting Python files
    for file in ("deploy.py", "lambda_handler.py", "main.py", "__init__.py"):
        src = Path(file)
        if src.exists():
            shutil.copy(src, PACKAGE_DIR)

    print("Creating deployment package...")

    # Create lambda-package.zip from lambda-package/
    shutil.make_archive(PACKAGE_DIR.name, "zip", PACKAGE_DIR)

    print(f"Deployment package created: {ZIP_FILE}")


if __name__ == "__main__":
    # Execute deployment package creation when run as a script
    deploy()
