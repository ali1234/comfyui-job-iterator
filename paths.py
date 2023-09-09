import pathlib
from folder_paths import folder_names_and_paths
from . import register_node


folder_types = tuple(sorted(folder_names_and_paths.keys()))
folder_default = "checkpoint" if "checkpoint" in folder_types else folder_types[0]

@register_node
class ModelFinder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filenames": ("SEQUENCE", ),
                "model_type": (folder_types, {"default": folder_default}),
                "recursive": ("BOOLEAN", {"default": True}),
                "skip_missing": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("SEQUENCE", "SEQUENCE")
    RETURN_NAMES = ("paths", "stems")
    FUNCTION = "go"
    CATEGORY = "ali1234/sequence"

    def find_models(self, fn, paths, recursive):
        if recursive:
            fn = f'**/{fn}'
        for p in paths:
            for f in p.glob(fn):
                return f.relative_to(p)
        return None

    def go(self, filenames, model_type, recursive, skip_missing):
        paths = [pathlib.Path(folder) for folder in folder_names_and_paths[model_type][0]]
        result = []
        for fn in filenames:
            f = self.find_models(fn, paths, recursive)
            if f is None:
                if skip_missing:
                    continue
                else:
                    raise Exception(f'Could not find file {fn}')
            result.append(f)

        return ([str(f) for f in result], [f.stem for f in result])
