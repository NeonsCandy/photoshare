import cloudinary
import cloudinary.uploader
from src.conf.config import settings

class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    @staticmethod
    def upload_photo(file, public_id: str):
        """Завантажує файл у Cloudinary і повертає відповідь з даними"""
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    @staticmethod
    def get_url(public_id, r):
        """Формує безпечне посилання на завантажене фото"""
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            version=r.get('version')
        )
        return src_url