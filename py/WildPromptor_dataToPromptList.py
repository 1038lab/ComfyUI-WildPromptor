import random
import re

class WildPromptor_DataToPromptList: 
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": False, "multiline": True, "tooltip": "Direct text input, will be processed along with file input"}),
                "separator": ("STRING", {"default": "","placeholder": "custom separator", "tooltip": "Separator for splitting text. default is empty for newline splitting"}),
                "batch_size": ("INT", {"default": 1, "min": 0, "max": 1000, "tooltip": "Number of prompts to generate. Set 0 for all"}),
                "count_start_from": ("INT", {"default": 1, "min": 1, "tooltip": "Starting index for prompt selection"}),
                "allow_duplicates": ("BOOLEAN", {"default": True, "tooltip": "Allow the same prompt to appear multiple times"}),
                "mode": (["⬇️Sequential", "⬆️Reverse", "🎲Random"], {"tooltip": "Prompt selection mode: Sequential, Reverse, or Random order"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "Random seed for reproducible results"}),
            },
            "optional": {
                "path": ("STRING", {"forceInput": True, "multiline": True, "tooltip": "File path input, will be processed along with text input"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("prompt_list", "prompt_combined",)
    OUTPUT_IS_LIST = (True, False,)
    FUNCTION = "generate_prompts"
    CATEGORY = "🧪AILab/🧿WildPromptor"

    def _split_and_clean(self, text, separator):
        """Split text by separator and clean the results."""
        if separator == "":
            segments = []
            for line in text.splitlines():
                line = line.rstrip(',').strip()
                if line:
                    segments.append(line)
        else:
            segments = [segment.strip() for segment in text.split(separator) if segment.strip()]
        return segments

    def _process_file_paths(self, path):
        """Process and validate file paths."""
        paths = re.split(r'\s*[,|\n]\s*', path.strip())
        cleaned_paths = []
        buffer = ""
        
        for part in paths:
            if part:
                buffer += part
                if buffer.count('.') > 1 or buffer.endswith(('.txt', '.csv')):
                    cleaned_paths.append(buffer.strip())
                    buffer = ""
        
        if buffer:
            cleaned_paths.append(buffer.strip())
            
        return cleaned_paths

    def _read_data(self, path, separator, text):
        """Read and process data from both file and text input."""
        data = []
        
        # Process direct text input
        if text:
            data.extend(self._split_and_clean(text, separator))

        # Process file input
        if path:
            for file_path in self._process_file_paths(path):
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data.extend(self._split_and_clean(f.read(), separator))
                    except (FileNotFoundError, IOError) as e:
                        print(f"Error reading file {file_path}: {e}")

        return data

    def generate_prompts(self, path, batch_size=1, count_start_from=1, seed=0, 
                        allow_duplicates=True, mode="⬇️Sequential", separator="", text=None):
        """Generate prompts based on input parameters."""
        random.seed(seed)
        
        # Read and process data
        data = self._read_data(path, separator, text)
        
        if not data:
            return (["No data available"], "No data available")
        
        # Handle batch size
        if batch_size == 0:
            batch_size = len(data)
        
        # Process data based on mode
        data_len = len(data)
        start_index = count_start_from - 1

        if mode == "⬆️Reverse":
            data = data[::-1]
        elif mode == "🎲Random":
            random.shuffle(data)

        # Generate prompts
        prompts = []
        used_indices = set()
        available_indices = list(range(start_index, data_len))
        
        for i in range(batch_size):
            if not available_indices:
                break
            
            if allow_duplicates:
                index = available_indices[i % len(available_indices)]
            else:
                if len(used_indices) >= len(available_indices):
                    break
                
                # Find next unused index
                attempts = 0
                max_attempts = len(available_indices)
                while attempts < max_attempts:
                    index = available_indices[(i + attempts) % len(available_indices)]
                    if index not in used_indices:
                        used_indices.add(index)
                        break
                    attempts += 1
                else:
                    # All indices used
                    break
                
            prompts.append(data[index])

        prompt_list = "\n\n".join(prompts)
        return (prompts, prompt_list,)

NODE_CLASS_MAPPINGS = {
    "WildPromptor_DataToPromptList": WildPromptor_DataToPromptList
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildPromptor_DataToPromptList": "Data To Prompt List 🔀+📋"
}
