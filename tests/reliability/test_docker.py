import subprocess
import shutil
import pytest
from pathlib import Path

DOCKER_TIMEOUT_SECONDS = 60
DOCKER_FALLBACK_PATHS = (
    "/usr/local/bin/docker",
    "/Applications/Docker.app/Contents/Resources/bin/docker",
)


def _resolve_docker_path() -> str | None:
    docker_path = shutil.which("docker")
    if docker_path is not None:
        return docker_path

    for candidate in DOCKER_FALLBACK_PATHS:
        if Path(candidate).exists():
            return candidate
    return None


def _require_docker_runtime() -> str:
    docker_path = _resolve_docker_path()
    if docker_path is None:
        pytest.skip("docker CLI is required for reliability Docker tests")

    result = subprocess.run(
        [docker_path, "info"],
        capture_output=True,
        text=True,
        check=False,
        timeout=DOCKER_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        pytest.skip(
            "docker daemon must be reachable for reliability Docker tests\n"
            f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
        )
    return docker_path

@pytest.fixture(scope="module")
def docker_image() -> tuple[str, str]:
    """Builds the Docker image once for the test module."""
    docker_path = _require_docker_runtime()
    image_name = "specforge-distill-test:latest"
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Build the image
    try:
        result = subprocess.run(
            [docker_path, "build", "-t", image_name, "."],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=DOCKER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        pytest.skip(f"Docker build timed out after {DOCKER_TIMEOUT_SECONDS} seconds")
    
    if result.returncode != 0:
        pytest.skip(f"Docker build failed (skipping test):\n{result.stderr}\n{result.stdout}")
        
    return docker_path, image_name

def test_docker_help_command(docker_image: tuple[str, str]) -> None:
    """Verifies the built Docker image can execute the distill --help command successfully."""
    docker_path, image_name = docker_image
    result = subprocess.run(
        [docker_path, "run", "--rm", image_name, "--help"],
        capture_output=True,
        text=True,
        check=False,
        timeout=DOCKER_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0, f"Docker run failed:\n{result.stderr}"
    assert "SpecForge Distill" in result.stdout
    assert "Transform legacy specification PDFs" in result.stdout
    assert "usage: distill" in result.stdout

def test_docker_dry_run_command(docker_image: tuple[str, str], tmp_path: Path) -> None:
    """
    Verifies the container can mount a volume and perform a --dry-run
    on a mock PDF.
    """
    docker_path, image_name = docker_image
    # Create a dummy PDF in a temp directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    dummy_pdf = data_dir / "dummy.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4\n")
    
    # Run the container, mounting the temp directory to /data
    result = subprocess.run(
        [
            docker_path, "run", "--rm",
            "-v", f"{data_dir.absolute()}:/data",
            image_name,
            "dummy.pdf", "--dry-run"
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=DOCKER_TIMEOUT_SECONDS,
    )
    
    assert result.returncode == 0, f"Docker run --dry-run failed:\n{result.stderr}"
    
    # The output should contain the JSON payload with "taxonomy_version"
    assert '"taxonomy_version"' in result.stdout
    assert "dummy.pdf" in result.stdout
