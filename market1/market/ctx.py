from typing import Dict


class SingletonMeta(type):
    _instances: Dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Ctx(metaclass=SingletonMeta):
    def __init__(self):
        self.mongo_client = None
        self.redis_client = None


ctx = Ctx()
