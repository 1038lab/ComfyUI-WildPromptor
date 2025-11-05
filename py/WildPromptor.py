import os
import random
import json
from typing import Tuple, List, Dict, Any

def get_subfolder_names():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    return [f for f in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, f)) and f != '__pycache__']

class BaseNode:
    _config = None

    @classmethod
    def load_config(cls):
        if cls._config is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
            with open(config_path, 'r') as f:
                cls._config = json.load(f)
        return cls._config

class PromptListNode(BaseNode):
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    OUTPUT_IS_LIST = (True,)
    
    # Class-level cache shared across all instances
    _file_contents_cache = {}

    def get_txt_file_names(self):
        return [f for f in os.listdir(self.data_path) if f.endswith(".txt")]
    
    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', self.FOLDER_NAME)
        self.file_names = self.get_txt_file_names()
        self.file_contents = self.load_file_contents()

    def load_file_contents(self):
        """Load file contents with class-level caching for better performance"""
        file_contents = {}
        for filename in self.file_names:
            file_path = os.path.join(self.data_path, filename)
            # Use class-level cache
            if file_path in self._file_contents_cache:
                file_contents[filename] = self._file_contents_cache[file_path]
            else:
                content = self.read_file_lines(filename)
                file_contents[filename] = content
                self._file_contents_cache[file_path] = content
        return file_contents

    def read_file_lines(self, filename):
        file_path = os.path.join(self.data_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]
                titles = []
                contents = []
                for line in lines:
                    if ' - ' in line:
                        title, content = line.split(' - ', 1)
                        titles.append(title)
                        contents.append(content)
                    else:
                        titles.append(line)
                        contents.append(line)
                return titles, contents
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return [], []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return [], []

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {"required": {}, "optional": {}}
        for filename in self.file_names:
            original_name = os.path.splitext(filename)[0]
            cleaned_name = original_name.split('.', 1)[-1] if '.' in original_name else original_name
            titles, contents = self.file_contents[filename]
            item_count = len(titles) if titles else len(contents)
            display_name = f"{cleaned_name} [{item_count}]"
            inputs["optional"][display_name] = (["❌disabled", "🎲Random", "🔢ordered"] + titles, {"default": "❌disabled"})

        inputs["optional"]["batch_size"] = ("INT", {"default": 1, "min": 1, "max": 1000})
        inputs["optional"]["allow_duplicates"] = ("BOOLEAN", {"default": False})
        inputs["optional"]["seed"] = ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})

        return inputs

    def process_prompt(self, batch_size=1, seed=0, allow_duplicates=False, **kwargs):
        random.seed(seed)
        all_prompts = []
        used_values_map = {}
        active_contents = {}

        for key, value in kwargs.items():
            if key in ["batch_size", "seed", "allow_duplicates"]:
                continue
            if value in ["🎲Random", "🔢ordered"]:
                cleaned_name = key.split(' [')[0]
                original_name = self.get_original_filename(cleaned_name)
                titles, contents = self.file_contents[original_name + '.txt']
                if contents:
                    active_contents[key] = contents
                    if not allow_duplicates:
                        used_values_map[key] = set()

        if not allow_duplicates and active_contents:
            max_possible_outputs = max(len(contents) for contents in active_contents.values())
            batch_size = min(batch_size, max_possible_outputs)

        for _ in range(batch_size):
            prompt_parts = []
            
            for key, value in kwargs.items():
                if key in ["batch_size", "seed", "allow_duplicates"]:
                    continue
                
                current_value = self._get_value_for_key(
                    key, value, active_contents, 
                    used_values_map, allow_duplicates, _
                )
                
                if current_value is not None:
                    prompt_parts.append(str(current_value))

            if prompt_parts:
                all_prompts.append(", ".join(prompt_parts))

        return (all_prompts,) if all_prompts else ([""],)

    def _get_value_for_key(self, key, value, active_contents, used_values_map, allow_duplicates, current_index):
        if value == "🎲Random":
            return self._handle_random_mode(
                key, active_contents, used_values_map, allow_duplicates
            )
        elif value == "🔢ordered":
            return self._handle_ordered_mode(
                key, active_contents, used_values_map, 
                allow_duplicates, current_index
            )
        elif value not in ["❌disabled", "🎲Random", "🔢ordered"]:
            return self._handle_specific_value(key, value)
        return None

    def _handle_random_mode(self, key, active_contents, used_values_map, allow_duplicates):
        if key not in active_contents:
            return None
            
        contents = active_contents[key]
        if allow_duplicates:
            return random.choice(contents)
            
        if len(used_values_map[key]) >= len(contents):
            used_values_map[key].clear()
            
        available_contents = [c for c in contents if c not in used_values_map[key]]
        if available_contents:
            chosen_value = random.choice(available_contents)
            used_values_map[key].add(chosen_value)
            return chosen_value
        return None

    def _handle_ordered_mode(self, key, active_contents, used_values_map, allow_duplicates, current_index):
        if key not in active_contents:
            return None
            
        contents = active_contents[key]
        index = current_index % len(contents)
        current_value = contents[index]
        
        if allow_duplicates:
            return current_value
            
        if len(used_values_map[key]) >= len(contents):
            used_values_map[key].clear()
            
        if current_value not in used_values_map[key]:
            used_values_map[key].add(current_value)
            return current_value
            
        for i in range(len(contents)):
            next_index = (index + i) % len(contents)
            next_value = contents[next_index]
            if next_value not in used_values_map[key]:
                used_values_map[key].add(next_value)
                return next_value
        return None

    def _handle_specific_value(self, key, value):
        cleaned_name = key.split(' [')[0]
        original_name = self.get_original_filename(cleaned_name)
        titles, contents = self.file_contents[original_name + '.txt']
        if titles and value in titles:
            index = titles.index(value)
            return contents[index]
        return None

    def get_original_filename(self, cleaned_name):
        for filename in self.file_names:
            if cleaned_name in filename:
                return os.path.splitext(filename)[0]
        return cleaned_name

class PromptConcatNode(BaseNode):
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    CATEGORY = "🧪AILab/🧿WildPromptor"

    @classmethod
    def INPUT_TYPES(cls):
        config = cls.load_config()
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config['data_path'])
        folders = config['folders']

        inputs = {
            "required": {},
            "optional": {
                "prefix": ("STRING", {"multiline": True, "default": ""})
            }
        }
        for folder in folders:
            if os.path.isdir(os.path.join(data_path, folder)):
                inputs["optional"][folder.lower()] = ("STRING", {"multiline": True, "default": ""})
        inputs["optional"].update({
            "suffix": ("STRING", {"multiline": True, "default": ""}),
            "separator": (["comma", "space", "newline"], {"default": "comma"}),
            "remove_duplicates": ("BOOLEAN", {"default": False}),
            "sort": ("BOOLEAN", {"default": False})
        })
        return inputs

    def process_prompt(self, prefix="", suffix="", separator="comma", remove_duplicates=False, sort=False, **kwargs):
        prompt_parts = [part.strip() for part in [prefix] + list(kwargs.values()) + [suffix] if part and part.strip()]
        
        if not prompt_parts:
            return ("",)
        
        if remove_duplicates:
            prompt_parts = list(dict.fromkeys(prompt_parts))
        
        if sort:
            middle_parts = prompt_parts[1:-1] if suffix else prompt_parts[1:]
            middle_parts.sort()
            prompt_parts = [prefix] + middle_parts + ([suffix] if suffix else [])
        
        final_prompt = {"comma": ", ", "space": " ", "newline": "\n"}[separator].join(prompt_parts)
        
        print(f"🔀 Prompt Concat output:\n{final_prompt}")
        
        return (final_prompt,)

class PromptBuilder:
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "content_only")
    OUTPUT_IS_LIST = (True, False)
    FUNCTION = "process_prompt"
    CATEGORY = "🧪AILab/🧿WildPromptor"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "prefix": ("STRING", {"multiline": True, "default": ""}),
                "content": ("STRING", {"multiline": True, "default": ""}),
                "suffix": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    def process_prompt(self, prefix: str = "", content: str = "", suffix: str = "") -> Tuple[List[str], str]:
        if isinstance(content, list):
            content = "\n".join(content)

        lines = content.split('\n') if content else []
        prompt_list = [f"{prefix}, {line}, {suffix}".strip(', ') for line in lines if line.strip()]

        return (prompt_list if prompt_list else [""], content)


class KeywordPicker:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("picked_keywords",)
    FUNCTION = "pick_keywords"
    CATEGORY = "🧪AILab/🧿WildPromptor"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "input_keywords": ("STRING", {"forceInput": True}),
                "keywords": ("STRING", {"multiline": True, "default": ""}),
                "pick_count": ("INT", {"default": 1, "min": 0, "max": 1000}),
                "pick_mode": (["🎲Random", "🔢ordered"], {"default": "🎲Random"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    def pick_keywords(self, input_keywords="", keywords="", pick_count=1, pick_mode="🎲Random", seed=0):
        # Combine and clean keywords
        parts = []
        if input_keywords and input_keywords.strip():
            parts.append(input_keywords.strip())
        if keywords and keywords.strip():
            parts.append(keywords.strip())
        
        if not parts:
            return ("",)
        
        combined = ", ".join(parts)
        keyword_list = [kw.strip() for kw in combined.split(',') if kw.strip()]

        if not keyword_list:
            return ("",)
        
        if pick_count <= 0:
            return ("",)
        
        if pick_mode == "🎲Random":
            random.seed(seed)
            picked = random.sample(keyword_list, min(pick_count, len(keyword_list)))
        else:
            picked = keyword_list[:pick_count]
        
        return (", ".join(picked),)

def create_Promptor_node(folder_name):
    return type(f"{folder_name.capitalize()}PromptorNode", (PromptListNode,), {
        "CATEGORY": "🧪AILab/🧿WildPromptor/📋Prompts List",
        "FOLDER_NAME": folder_name
    })

NODE_CLASS_MAPPINGS = {
    "PromptConcat": PromptConcatNode,
    "PromptBuilder": PromptBuilder,
    "KeywordPicker": KeywordPicker,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptConcat": "Prompt Concat 🔀",
    "PromptBuilder": "Prompt Builder 🔀",
    "KeywordPicker": "Keyword Picker 🔀",
}

for folder in get_subfolder_names():
    node_class = create_Promptor_node(folder)
    NODE_CLASS_MAPPINGS[f"{folder.capitalize()} 📋"] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[f"{folder.capitalize()} 📋"] = f"{folder.capitalize()} 📋"