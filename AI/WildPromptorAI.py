import os
import json
import re
from PIL import Image
import numpy as np
import base64

class WildPromptorAI:
    @staticmethod
    def tensor_to_image(tensor):
        tensor = tensor.cpu().clamp(0, 1).mul(255).byte().numpy()
        if tensor.ndim == 4:
            tensor = tensor.squeeze(0)
        if tensor.ndim == 3:
            if tensor.shape[0] == 1:
                tensor = np.repeat(tensor[0], 3, axis=0)
            elif tensor.shape[0] == 3:
                tensor = np.transpose(tensor, (1, 2, 0))
        elif tensor.ndim == 2:
            tensor = np.stack([tensor] * 3, axis=-1)
        return Image.fromarray(tensor, mode='RGB')

    @staticmethod
    def INPUT_TYPES():
        return {
            "required": {"keywords": ("STRING", {"multiline": True})},
            "optional": {"max_length": ("INT", {"default": 512, "min": 50, "max": 1000})}
        }
    def __init__(self):
        self.load_config()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config_ai.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            print(f"Config file not found at: {config_path}")
            self.config = {}

    def clean_prompt(self, text):
        text = re.sub(r'^(The (image|picture|photo|scene|snapshot) (is|shows|displays|depicts|contains|features|presents|captures|portrays|reveals))\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^.*?:\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*+', '', text)
        text = ' '.join(text.split())
        unwanted_phrases = [
            'style', 'additional detail', 'artistic style', 'optional details', 
            'generate an image of', 'image description:', 'the image displayed is', 
            'the image shows', 'in this image', 'the scene depicts', 
            'this image portrays', 'visualize a scene where', 'the photograph shows',
            'the picture displays', 'we can see', 'visible in the image'
        ]
        pattern = r'\b(' + '|'.join(map(re.escape, unwanted_phrases)) + r')\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text.strip()

    def format_prompt(self, keywords):
        return f"Based on these keywords: {keywords}\nCreate a single, concise paragraph describing an image. Focus only on the visual elements without mentioning prompt creation or image generation. Avoid sections, bullet points, or style suggestions."

    def format_image_prompt(self, keywords):
        if keywords.strip():
            return f"Analyze the image based on these keywords and questions: {keywords}. Describe the image in detail, focusing on visual elements, colors, composition, and any notable objects or features. Also, specifically address any questions or points mentioned in the keywords. Provide a comprehensive description without using phrases like 'The image shows' or 'The image contains'."
        else:
            return "Describe the image in detail, focusing on visual elements, colors, composition, and any notable objects or features. Provide a comprehensive description without using phrases like 'The image shows' or 'The image contains'."
            
    def generate_prompt(self, keywords, max_length=512):
        raise NotImplementedError("Subclasses must implement generate_prompt method")