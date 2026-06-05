import shutil
import subprocess
import zipfile
from pathlib import Path

# Build artifacts
PACKAGE_DIR = Path("lambda-package")
ZIP_FILE = Path("lambda-package.zip")


def cleanup_package():
    """
    Remove files that are not required at runtime to reduce
    the Lambda deployment package size.
    """
    print("Removing unnecessary files...")

    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.dist-info",
        "**/*.egg-info",
        "**/tests",
        "**/test",
    ]

    for pattern in patterns:
        for path in PACKAGE_DIR.glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)
            except Exception as ex:
                print(f"Warning: Could not remove {path}: {ex}")


def create_zip():
    """
    Create a compressed deployment package.
    """
    print("Creating deployment package...")

    with zipfile.ZipFile(
        ZIP_FILE,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zip_file:
        for file in PACKAGE_DIR.rglob("*"):
            zip_file.write(file, file.relative_to(PACKAGE_DIR))

    size_mb = ZIP_FILE.stat().st_size / (1024 * 1024)
    print(f"Deployment package created: {ZIP_FILE}")
    print(f"Package size: {size_mb:.2f} MB")


def deploy():
    """
    Build an AWS Lambda deployment package.

    Steps:
    1. Remove previous build artifacts.
    2. Install dependencies using the AWS Lambda Python container.
    3. Copy source code and supporting files.
    4. Remove unnecessary files.
    5. Create a compressed ZIP package.
    """

    # Clean previous build
    shutil.rmtree(PACKAGE_DIR, ignore_errors=True)
    ZIP_FILE.unlink(missing_ok=True)

    # Create package directory
    PACKAGE_DIR.mkdir(parents=True)

    print("Installing dependencies for AWS Lambda...")

    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{Path.cwd()}:/var/task",
            "-w",
            "/var/task",
            "--platform",
            "linux/amd64",
            "--entrypoint",
            "/bin/sh",
            "public.ecr.aws/lambda/python:3.12",
            "-c",
            (
                "pip install "
                "-r requirements.txt "
                "-t lambda-package "
                "--platform manylinux2014_x86_64 "
                "--only-binary=:all: "
                "--no-cache-dir "
                "--upgrade"
            ),
        ],
        check=True,
    )

    # Copy application folders
    for folder in ("data", "src"):
        src = Path(folder)
        if src.exists():
            print(f"Copying {folder}/")
            shutil.copytree(src, PACKAGE_DIR / folder)

    # Copy Lambda entry-point files
    for file_name in (
        "lambda_handler.py",
        "main.py",
        "__init__.py",
    ):
        file_path = Path(file_name)
        if file_path.exists():
            print(f"Copying {file_name}")
            shutil.copy(file_path, PACKAGE_DIR)

    # Remove unnecessary files
    cleanup_package()

    # Create zip
    create_zip()


if __name__ == "__main__":
    deploy()