from WildPromptorAI import WildPromptorAI
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import os

class WildPromptor_HFgpt(WildPromptorAI):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "keywords": ("STRING", {"multiline": True}),
                "model_repo": (cls.get_hfgpt_repos(),),
                "max_length": ("INT", {"default": 1024, "min": 1, "max": 4096, "step": 1}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "🧪AILab/🤖AI"

    @classmethod
    def get_hfgpt_repos(cls):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config_ai.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            repos = config.get('HFGPT_repos', [])
            return repos if repos else ["No models found"]
        except Exception as e:
            print(f"Error loading HFGPT repos: {str(e)}")
            return ["Configuration loading failed"]

    def __init__(self):
        super().__init__()
        self.models = {}
        self.tokenizers = {}

    def generate_prompt(self, keywords, model_repo, temperature=0.7, max_length=256):
        if model_repo not in self.models:
            self.models[model_repo] = AutoModelForCausalLM.from_pretrained(model_repo)
            self.tokenizers[model_repo] = AutoTokenizer.from_pretrained(model_repo)
            self.models[model_repo].eval()

        prompt = self.format_prompt(keywords)
        input_ids = self.tokenizers[model_repo](prompt, return_tensors='pt').input_ids

        outputs = self.models[model_repo].generate(
            input_ids,
            max_length=max_length,
            num_return_sequences=1,
            temperature=temperature,
            do_sample=True,
            no_repeat_ngram_size=2
        )

        generated_prompt = self.tokenizers[model_repo].decode(outputs[0], skip_special_tokens=True)
        generated_prompt = self.clean_prompt(generated_prompt)

        print(f"[HuggingFace GPT prompt]:\n{generated_prompt}")
        return (generated_prompt,)

NODE_CLASS_MAPPINGS = {"WildPromptor_HFgpt}
NODE_DISPLAY_NAME_MAPPINGS = {"WildPromptor_HFgpt": "HuggingFace GPT 🤖(WildPromptor)"}