import torch

from . import register_node


@register_node
class Stringify:
    """Convert any input to str/repr."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "x": ("*", ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("str", "repr")
    FUNCTION = "go"
    CATEGORY = "ali1234/debug"

    def go(self, x):
        return (str(x), repr(x))


@register_node
class JoinImageBatch:
    """Turns an image batch into one big image."""
    @classmethod
    def INPUT_TYPES(s):
        """
            Joins an image batch into a single image.
        """
        return {
            "required": {
                "images": ("IMAGE",),
                "mode": (("horizontal", "vertical"), {"default": "horizontal"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "join"
    CATEGORY = "ali1234/image"

    def join(self, images, mode):
        n, h, w, c = images.shape
        image = None
        if mode == "vertical":
            # for vertical we can just reshape
            image = images.reshape(1, n * h, w, c)
        elif mode == "horizontal":
            # for horizontal we have to swap axes
            image = torch.transpose(torch.transpose(images, 1, 2).reshape(1, n * w, h, c), 1, 2)
        return (image,)


@register_node
class SelectImageBatch:
    """Selects one image from an image batch."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "select": ("INT", {"default": 0, "min": 0, "max": 99999, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "select"
    CATEGORY = "ali1234/image"

    def select(self, images, select):
        n, h, w, c = images.shape
        if select >= n:
            select = n - 1
        return (images[select].reshape(1, h, w, c),)
