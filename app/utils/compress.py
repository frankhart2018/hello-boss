import tarfile
import os


def create_tarball(output_filename: str, source_dir: str) -> None:
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
