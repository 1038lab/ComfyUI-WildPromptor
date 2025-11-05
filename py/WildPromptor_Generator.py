import os
import random
import json
from typing import Tuple, List, Dict, Any

class WildPromptor_AllInOneList:
    RETURN_TYPES = ("DPROMPT_DATA",)
    RETURN_NAMES = ("selected_options",)
    FUNCTION = "select_options"
    CATEGORY = "🧪AILab/🧿WildPromptor/📋Prompts List"
    
    # Class-level cache shared across all instances
    _file_cache = {}

    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config['data_path'])

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {"required": {}, "optional": {}}
        
        for folder in self.config['folders']:
            folder_path = os.path.join(self.data_path, folder)
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith('.txt'):
                        original_name = os.path.splitext(file)[0]
                        cleaned_name = original_name.split('.', 1)[-1] if '.' in original_name else original_name
                        file_path = os.path.join(folder_path, file)
                        options = self.read_file_options(file_path)
                        item_count = len(options)
                        display_name = f"{folder} - {cleaned_name} [{item_count}]"
                        inputs["optional"][display_name] = (["❌disabled", "🎲Random", "🔢ordered"] + options, {"default": "❌disabled"})
        
        return inputs

    def read_file_options(self, file_path: str) -> List[str]:
        """Read file options with class-level caching for better performance"""
        if file_path in self._file_cache:
            return self._file_cache[file_path]
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                options = [line.strip() for line in file if line.strip()]
            self._file_cache[file_path] = options
            return options
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []

    def select_options(self, **kwargs):
        selected_options = {k: v for k, v in kwargs.items() if v != "❌disabled"}
        if not selected_options:
            print("Warning: No options selected.")
        return (selected_options,)

class WildPromptor_Generator:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "🧪AILab/🧿WildPromptor"
    
    # Class-level cache shared across all instances  
    _file_cache = {}

    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config['data_path'])

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "selected_options": ("DPROMPT_DATA",),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 1000}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "allow_duplicates": ("BOOLEAN", {"default": True}),
            }
        }

    def process_prompt(self, selected_options: Dict[str, Any], batch_size: int, seed: int, allow_duplicates: bool = True) -> Tuple[List[str]]:
        random.seed(seed)
        all_prompts = []

        for i in range(batch_size):
            prompt_parts = []
            for key, value in selected_options.items():
                if value == "🎲Random":
                    folder, file_info = key.rsplit(' - ', 1)
                    cleaned_name = file_info.split(' [')[0]
                    original_name = self.get_original_filename(folder, cleaned_name)
                    file_path = os.path.join(self.data_path, folder, f"{original_name}.txt")
                    options = self.read_file_options(file_path)
                    if options:
                        if allow_duplicates:
                            prompt_parts.append(random.choice(options))
                        else:
                            prompt_parts.append(random.sample(options, 1)[0])
                elif value == "🔢ordered":
                    folder, file_info = key.rsplit(' - ', 1)
                    cleaned_name = file_info.split(' [')[0]
                    original_name = self.get_original_filename(folder, cleaned_name)
                    file_path = os.path.join(self.data_path, folder, f"{original_name}.txt")
                    options = self.read_file_options(file_path)
                    if options:
                        index = i % len(options)
                        prompt_parts.append(options[index])
                elif value != "❌disabled":
                    prompt_parts.append(str(value))
            
            if prompt_parts:
                all_prompts.append(", ".join(prompt_parts))

        for prompt in all_prompts:
            print(f"🔀 WildPromptor Generator output: {prompt}")

        return (all_prompts,)

    def get_original_filename(self, folder, cleaned_name):
        folder_path = os.path.join(self.data_path, folder)
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt') and cleaned_name.split(' [')[0] in filename:
                return os.path.splitext(filename)[0]
        return cleaned_name.split(' [')[0]

    def read_file_options(self, file_path: str) -> List[str]:
        """Read file options with class-level caching for better performance"""
        if file_path in self._file_cache:
            return self._file_cache[file_path]
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                options = [line.strip() for line in file if line.strip()]
            self._file_cache[file_path] = options
            return options
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []

NODE_CLASS_MAPPINGS = {
    "WildPromptor_AllInOneList": WildPromptor_AllInOneList,
    "WildPromptor_Generator": WildPromptor_Generator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildPromptor_AllInOneList": "All-In-One List 📋",
    "WildPromptor_Generator": "WildPromptor Generator 🔀"
}