import torch
import numpy as np

from . import register_node


@register_node
class JoinImageBatch:
    """Turns an image batch into one big image."""
    @classmethod
    def INPUT_TYPES(s):
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
class JoinImages:
    """Turns joins two images into one big image."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "mode": (("horizontal", "vertical"), {"default": "horizontal"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "join"
    CATEGORY = "ali1234/image"

    def join(self, image_a, image_b, mode):
        dim = {'horizontal': 2, 'vertical': 1}[mode]
        return (torch.concat((image_a, image_b), dim), )


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


@register_node
class GetImageSize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "batch_size")
    FUNCTION = "go"
    CATEGORY = "ali1234/image"

    def go(self, images):
        return (images.shape[2], images.shape[1], images.shape[0])





@register_node
class StringToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "Hello world!"}),
                "width": ("INT", {"default": 384}),
                "height": ("INT", {"default": 16}),
                "colour": ("COLOR", {"default": "white"}),
                "background": ("COLOR", {"default": "black"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "render"
    CATEGORY = "ali1234/image"

    def render(self, text, width, height, colour, background):
        from PIL import Image, ImageDraw, ImageFont
        font = ImageFont.load_default()
        img = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(img)
        _, _, w, h = draw.textbbox((0, 0), text, font=font)
        draw.text(((width - w) / 2, ((height - h) / 2) - 1), text, font=font, fill=colour)
        tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)
        return (tensor,)


@register_node
class ProgressBar:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "progress": ("FLOAT", {'default': 0, 'forceInput': True}),
                "padding": ("INT", {'default': 3}),
                "width": ("INT", {"default": 384}),
                "height": ("INT", {"default": 16}),
                "colour": ("COLOR", {"default": "white"}),
                "background": ("COLOR", {"default": "black"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "render"
    CATEGORY = "ali1234/image"

    def render(self, progress, padding, width, height, colour, background):
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(img)
        draw.rectangle((padding, padding, width - padding - 1, height - padding - 1), outline=colour)
        if progress > 0:
            ip = padding + 2
            draw.rectangle((ip, ip, max(ip+1, (width - ip - 1) * progress), height - ip - 1), outline=colour, fill=colour)
        tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)
        return (tensor,)
