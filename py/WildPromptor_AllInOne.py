import os
import random
import json
from typing import Tuple, List, Dict, Any

class WildPromptor_AllInOne:
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

    def read_file_options(self, file_path):
        """Read file options with class-level caching"""
        if file_path in self._file_cache:
            return self._file_cache[file_path]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                options = [line.strip() for line in f if line.strip()]
            self._file_cache[file_path] = options
            return options
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {
            "required": {},
            "optional": {
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 1000}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "allow_duplicates": ("BOOLEAN", {"default": True}),
            }
        }

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

    def process_prompt(self, batch_size: int = 1, seed: int = 0, allow_duplicates: bool = True, **kwargs):
        random.seed(seed)
        all_prompts = []
        used_values_map = {}  # Track used values for each category when not allowing duplicates

        # Prepare active contents
        active_contents = {}
        for key, value in kwargs.items():
            if key in ["batch_size", "seed", "allow_duplicates"] or value == "❌disabled":
                continue
            
            if value in ["🎲Random", "🔢ordered"]:
                folder, cleaned_name = key.split(' - ', 1)
                original_name = self.get_original_filename(folder, cleaned_name.split(' [')[0])
                file_path = os.path.join(self.data_path, folder, f"{original_name}.txt")
                options = self.read_file_options(file_path)
                if options:
                    active_contents[key] = {'options': options, 'mode': value}
                    if not allow_duplicates:
                        used_values_map[key] = set()

        for i in range(batch_size):
            prompt_parts = []
            
            for key, value in kwargs.items():
                if key in ["batch_size", "seed", "allow_duplicates"] or value == "❌disabled":
                    continue
                
                if key in active_contents:
                    data = active_contents[key]
                    options = data['options']
                    mode = data['mode']
                    
                    if mode == "🎲Random":
                        if allow_duplicates:
                            prompt_parts.append(random.choice(options))
                        else:
                            # Check if all values are used
                            if len(used_values_map[key]) >= len(options):
                                used_values_map[key].clear()
                            
                            available = [opt for opt in options if opt not in used_values_map[key]]
                            if available:
                                chosen = random.choice(available)
                                used_values_map[key].add(chosen)
                                prompt_parts.append(chosen)
                    
                    elif mode == "🔢ordered":
                        index = i % len(options)
                        current_value = options[index]
                        
                        if allow_duplicates:
                            prompt_parts.append(current_value)
                        else:
                            # Try to find an unused value
                            if len(used_values_map[key]) >= len(options):
                                used_values_map[key].clear()
                            
                            if current_value not in used_values_map[key]:
                                used_values_map[key].add(current_value)
                                prompt_parts.append(current_value)
                            else:
                                # Find next unused value
                                for j in range(len(options)):
                                    next_idx = (index + j) % len(options)
                                    next_val = options[next_idx]
                                    if next_val not in used_values_map[key]:
                                        used_values_map[key].add(next_val)
                                        prompt_parts.append(next_val)
                                        break
                else:
                    # Specific value selected
                    folder, cleaned_name = key.split(' - ', 1)
                    original_name = self.get_original_filename(folder, cleaned_name.split(' [')[0])
                    file_path = os.path.join(self.data_path, folder, f"{original_name}.txt")
                    options = self.read_file_options(file_path)
                    if value in options:
                        prompt_parts.append(value)

            if prompt_parts:
                all_prompts.append(", ".join(prompt_parts))

        for prompt in all_prompts:
            print(f"🔀 WildPromptor All-in-One prompt: {prompt}")

        return (all_prompts,) if all_prompts else ([""],)

    def get_original_filename(self, folder, cleaned_name):
        folder_path = os.path.join(self.data_path, folder)
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt') and cleaned_name in filename:
                return os.path.splitext(filename)[0]
        return cleaned_name

NODE_CLASS_MAPPINGS = {
    "WildPromptor_AllInOne": WildPromptor_AllInOne
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildPromptor_AllInOne": "WildPromptor All-in-One 📋+🔀"
}