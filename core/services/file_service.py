import os
from uuid import uuid1

from core.dataclasses.user_dataclass import ProfileDataClass


class FileService:
    @staticmethod
    def upload_avatar(instance: ProfileDataClass, file: str):
        ext = file.split('.')[-1]
        return os.path.join(instance.last_name, 'avatars', f'{uuid1()}.{ext}')