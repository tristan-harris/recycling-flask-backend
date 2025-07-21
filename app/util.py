from pathlib import Path

from PIL import Image, UnidentifiedImageError
import pillow_heif
from werkzeug.datastructures import FileStorage

# required for the HEIC images that are created by Apple devices
pillow_heif.register_heif_opener()

# used for getting submission, reward and bin images
def get_image_upload_path(id:int, uploads_directory:str, uploads_subdirectory:str) -> Path:
    uploads_directory_path = Path(uploads_directory)
    if not uploads_directory_path.exists():
        uploads_directory_path.mkdir()

    images_directory = uploads_directory_path.joinpath(uploads_subdirectory)
    if not images_directory.exists():
        images_directory.mkdir()

    return images_directory.joinpath(f"{id}.jpg")

# PIL automatically converts image based on file extension (EXIF data is also discarded)
def process_image(image_file:FileStorage, image_path:Path):
    try:
        with Image.open(image_file.stream) as pil_image:
            pil_image.save(image_path)
    except UnidentifiedImageError as e:
        raise e
    except OSError as e:
        raise e
