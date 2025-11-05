import requests
import os

class WildPromptor_ShowPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
                "pnginfo": "EXTRA_PNGINFO",
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "show"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "🧪AILab/🧿WildPromptor"

    def show(self, prompt, node_id=None, pnginfo=None):
        if node_id is not None and pnginfo is not None:
            if isinstance(pnginfo, list) and pnginfo and isinstance(pnginfo[0], dict):
                workflow = pnginfo[0].get("workflow")
                if workflow and "nodes" in workflow:
                    for n in workflow["nodes"]:
                        if str(n.get("id")) == str(node_id[0]):
                            n["widgets_values"] = prompt
        
        return {"ui": {"prompt": prompt}, "result": (prompt,)}

class WildPromptor_TextInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_text"
    CATEGORY = "🧪AILab/🧿WildPromptor"

    def get_text(self, text):
        return (text,)


NODE_CLASS_MAPPINGS = {
    "WildPromptor_ShowPrompt": WildPromptor_ShowPrompt,
    "WildPromptor_TextInput": WildPromptor_TextInput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildPromptor_ShowPrompt": "Show Prompt 📃",
    "WildPromptor_TextInput": "Text Input ⌨️",
}