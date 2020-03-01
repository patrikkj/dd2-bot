# JSON
name_to_class = {}

def json_serializable(cls):
    name_to_class[cls.__name__] = cls
    setattr(cls, '__serializing_cls_name__', cls.__name__)
    return cls
