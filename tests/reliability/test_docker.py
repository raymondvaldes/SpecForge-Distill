import subprocess
import shutil
import pytest
from pathlib import Path

# Skip these tests if Docker is not installed or the daemon isn't running
DOCKER_AVAILABLE = shutil.which("docker") is not None

def _is_docker_running() -> bool:
    if not DOCKER_AVAILABLE:
        return False
    try:
        # Check if we can contact the docker daemon
        result = subprocess.run(
            ["docker", "info"], 
            capture_output=True, 
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False

pytestmark = pytest.mark.skipif(
    not _is_docker_running(),
    reason="Docker is not installed or the daemon is not running on this machine"
)

@pytest.fixture(scope="module")
def docker_image() -> str:
    """Builds the Docker image once for the test module."""
    image_name = "specforge-distill-test:latest"
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Build the image
    result = subprocess.run(
        ["docker", "build", "-t", image_name, "."],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.returncode != 0:
        pytest.fail(f"Docker build failed:\n{result.stderr}\n{result.stdout}")
        
    return image_name

def test_docker_help_command(docker_image: str) -> None:
    """Verifies the built Docker image can execute the distill --help command successfully."""
    result = subprocess.run(
        ["docker", "run", "--rm", docker_image, "--help"],
        capture_output=True,
        text=True,
        check=False
    )
    
    assert result.returncode == 0, f"Docker run failed:\n{result.stderr}"
    assert "SpecForge Distill" in result.stdout
    assert "Transform legacy specification PDFs" in result.stdout
    assert "usage: distill" in result.stdout

def test_docker_dry_run_command(docker_image: str, tmp_path: Path) -> None:
    """
    Verifies the container can mount a volume and perform a --dry-run
    on a mock PDF.
    """
    # Create a dummy PDF in a temp directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    dummy_pdf = data_dir / "dummy.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4\n")
    
    # Run the container, mounting the temp directory to /data
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{data_dir.absolute()}:/data",
            docker_image,
            "dummy.pdf", "--dry-run"
        ],
        capture_output=True,
        text=True,
        check=False
    )
    
    assert result.returncode == 0, f"Docker run --dry-run failed:\n{result.stderr}"
    
    # The output should contain the JSON payload with "taxonomy_version"
    assert '"taxonomy_version"' in result.stdout
    assert "dummy.pdf" in result.stdout
