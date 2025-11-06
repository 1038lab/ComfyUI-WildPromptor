import os
import torch
from transformers import AutoTokenizer, AutoModel
from torchvision.transforms import ToPILImage
from PIL import Image
import folder_paths
from typing import List

class WildPromptor_Minicpm:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "inference"
    CATEGORY = "🧪AILab/🤖AI"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "model": (["MiniCPM-V-2_6-int4", "MiniCPM-Llama3-V-2_5-int4","MiniCPM-V-4-int4","MiniCPM-V-4_5-int4"], {"default": "MiniCPM-V-2_6-int4"}),
                "language": (["Auto", "English", "Chinese", "Japanese", "Korean"], {"default": "Auto"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0, "max": 1, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "image": ("IMAGE",),
            },
        }

    def __init__(self):
        self.device = "cpu"
        self.bf16_support = False
        self.use_cuda = False
        
        try:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                self.use_cuda = True
                self.bf16_support = torch.cuda.get_device_capability(self.device)[0] >= 8
        except Exception as e:
            print(f"WildPromptor_minicpm CUDA init warning: {str(e)}")
            
        self.tokenizer = None
        self.model = None

    def process_image(self, image_tensor):
        if image_tensor.dim() == 4:
            if image_tensor.shape[-1] == 3:
                image_tensor = image_tensor.permute(0, 3, 1, 2)
            return [ToPILImage()(img) for img in image_tensor]
        elif image_tensor.dim() == 3:
            if image_tensor.shape[-1] == 3:
                image_tensor = image_tensor.permute(2, 0, 1)
            return [ToPILImage()(image_tensor)]
        else:
            raise ValueError(f"Unsupported image tensor shape: {image_tensor.shape}")

    def get_language_prompt(self, language, text):
        language_prompts = {
            "English": "Please respond in English: ",
            "Chinese": "请用中文回答: ",
            "Japanese": "日本語で答えてください: ",
            "Korean": "한국어로 답변해주세요: ",
            "Auto": ""
        }
        return language_prompts.get(language, "") + text

    def inference(self, text, model, language, temperature, seed, image=None):
        if seed > 0:
            torch.manual_seed(seed)

        try:
            current_model_id = f"openbmb/{model}"
            model_path = os.path.join(folder_paths.models_dir, "LLM", os.path.basename(current_model_id))

            if self.model is None or not hasattr(self, 'loaded_model_name') or self.loaded_model_name != current_model_id:
                if self.model is not None:
                    del self.model
                    del self.tokenizer
                    if self.use_cuda:
                        torch.cuda.empty_cache()
                
                print(f"Loading model: {current_model_id}")
                
                if not os.path.exists(model_path):
                    from huggingface_hub import snapshot_download
                    print(f"Downloading model to: {model_path}")
                    snapshot_download(repo_id=current_model_id, local_dir=model_path, local_dir_use_symlinks=False)

                self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
                model_kwargs = {
                    "trust_remote_code": True,
                    "attn_implementation": "sdpa"
                }

                if self.use_cuda:
                    model_kwargs["dtype"] = torch.bfloat16 if self.bf16_support else torch.float16

                self.model = AutoModel.from_pretrained(model_path, **model_kwargs)
                
                if self.use_cuda:
                    self.model = self.model.to(self.device)
                
                self.model.eval()
                self.loaded_model_name = current_model_id
            
            with torch.no_grad():
                if image is not None:
                    try:
                        if isinstance(image, torch.Tensor):
                            images = self.process_image(image)
                            content_list = images + [self.get_language_prompt(language, text)]
                            msgs = [{"role": "user", "content": content_list}]
                        else:
                            raise ValueError("Image must be a tensor")
                    except Exception as e:
                        return (f"Image processing error: {str(e)}",)
                else:
                    msgs = [{"role": "user", "content": [self.get_language_prompt(language, text)]}]

                result = self.model.chat(
                    image=None,
                    msgs=msgs,
                    tokenizer=self.tokenizer,
                    sampling=True,
                    temperature=temperature,
                    max_new_tokens=2048
                )

                if self.use_cuda:
                    torch.cuda.empty_cache()

                return (result,)

        except Exception as e:
            return (f"Error: {str(e)}",)

NODE_CLASS_MAPPINGS = {
    "WildPromptor_Minicpm": WildPromptor_Minicpm
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildPromptor_Minicpm": "MiniCPM 🤖👁️(WildPromptor)"
}