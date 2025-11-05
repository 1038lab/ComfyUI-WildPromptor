import os
import json

class CustomListManager:
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status", "file_list")
    FUNCTION = "manage_list"
    CATEGORY = "🧪AILab/🧿WildPromptor/📋Prompts List"
    
    def __init__(self):
        self.custom_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Custom')
        if not os.path.exists(self.custom_path):
            os.makedirs(self.custom_path)
    
    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        custom_files = self.get_custom_files()
        file_options = ["<Select File>"] + custom_files if custom_files else ["<No Custom Files>"]
        
        return {
            "required": {
                "action": ([
                    "📝 Create New List",
                    "✏️ Edit List (Replace All)",
                    "➕ Add Line",
                    "➖ Remove Line",
                    "📋 View List",
                    "🗑️ Delete List",
                ], {"default": "📝 Create New List"}),
            },
            "optional": {
                "file_name": ("STRING", {"default": "My_Custom_List", "multiline": False}),
                "select_file": (file_options, {"default": file_options[0]}),
                "content": ("STRING", {"default": "", "multiline": True}),
                "line_text": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    def get_custom_files(self):
        if not os.path.exists(self.custom_path):
            return []
        files = [f for f in os.listdir(self.custom_path) if f.endswith('.txt')]
        return sorted(files)
    
    def safe_filename(self, filename):
        safe_name = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        safe_name = safe_name.strip()
        if not safe_name.endswith('.txt'):
            safe_name += '.txt'
        return safe_name
    
    def get_file_path(self, filename):
        safe_name = self.safe_filename(filename)
        file_path = os.path.join(self.custom_path, safe_name)
        real_path = os.path.realpath(file_path)
        real_custom = os.path.realpath(self.custom_path)
        if not real_path.startswith(real_custom):
            raise ValueError("Security Error: Can only operate files in data/Custom/ folder")
        return file_path
    
    def manage_list(self, action, file_name="", select_file="<Select File>", content="", line_text=""):
        try:
            target_file = select_file if select_file not in ["<Select File>", "<No Custom Files>"] else file_name
            
            if action == "📝 Create New List":
                return self.create_list(file_name, content)
            
            elif action == "✏️ Edit List (Replace All)":
                return self.edit_list(target_file, content)
            
            elif action == "➕ Add Line":
                return self.add_line(target_file, line_text)
            
            elif action == "➖ Remove Line":
                return self.remove_line(target_file, line_text)
            
            elif action == "📋 View List":
                return self.view_list(target_file)
            
            elif action == "🗑️ Delete List":
                return self.delete_list(target_file)
            
            else:
                return (f"❌ 未知操作: {action}", self.get_file_list_string())
        
        except Exception as e:
            return (f"❌ 错误: {str(e)}", self.get_file_list_string())
    
    def create_list(self, filename, content):
        if not filename or filename.strip() == "":
            return ("❌ Error: Please provide filename", self.get_file_list_string())
        file_path = self.get_file_path(filename)
        if os.path.exists(file_path):
            return (f"❌ Error: File already exists: {os.path.basename(file_path)}", self.get_file_list_string())
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        line_count = len([line for line in content.strip().split('\n') if line.strip()])
        return (f"✅ Created: {os.path.basename(file_path)} ({line_count} lines)", self.get_file_list_string())
    
    def edit_list(self, filename, content):
        if not filename or filename in ["<Select File>", "<No Custom Files>"]:
            return ("❌ Error: Please select or input filename", self.get_file_list_string())
        file_path = self.get_file_path(filename)
        if not os.path.exists(file_path):
            return (f"❌ Error: File not found: {os.path.basename(file_path)}", self.get_file_list_string())
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        line_count = len([line for line in content.strip().split('\n') if line.strip()])
        return (f"✅ Updated: {os.path.basename(file_path)} ({line_count} lines)", self.get_file_list_string())
    
    def add_line(self, filename, line_text):
        if not filename or filename in ["<Select File>", "<No Custom Files>"]:
            return ("❌ Error: Please select or input filename", self.get_file_list_string())
        if not line_text or line_text.strip() == "":
            return ("❌ Error: Please input content to add", self.get_file_list_string())
        file_path = self.get_file_path(filename)
        if not os.path.exists(file_path):
            return (f"❌ Error: File not found: {os.path.basename(file_path)}", self.get_file_list_string())
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content and not content.endswith('\n'):
            content += '\n'
        content += line_text.strip() + '\n'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return (f"✅ Added to: {os.path.basename(file_path)}\nContent: {line_text.strip()}", self.get_file_list_string())
    
    def remove_line(self, filename, line_text):
        if not filename or filename in ["<Select File>", "<No Custom Files>"]:
            return ("❌ Error: Please select or input filename", self.get_file_list_string())
        if not line_text or line_text.strip() == "":
            return ("❌ Error: Please input content to remove", self.get_file_list_string())
        file_path = self.get_file_path(filename)
        if not os.path.exists(file_path):
            return (f"❌ Error: File not found: {os.path.basename(file_path)}", self.get_file_list_string())
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        target = line_text.strip()
        original_count = len(lines)
        filtered_lines = [line for line in lines if line.strip() != target]
        removed_count = original_count - len(filtered_lines)
        if removed_count == 0:
            return (f"⚠️ Line not found: {target}", self.get_file_list_string())
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(filtered_lines)
        return (f"✅ Removed {removed_count} line(s): {target}", self.get_file_list_string())
    
    def view_list(self, filename):
        if not filename or filename in ["<Select File>", "<No Custom Files>"]:
            return ("❌ Error: Please select or input filename", self.get_file_list_string())
        file_path = self.get_file_path(filename)
        if not os.path.exists(file_path):
            return (f"❌ Error: File not found: {os.path.basename(file_path)}", self.get_file_list_string())
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = [line for line in content.split('\n') if line.strip()]
        line_count = len(lines)
        view_content = f"📄 {os.path.basename(file_path)} ({line_count} lines)\n" + "=" * 50 + "\n" + content
        return (view_content, self.get_file_list_string())
    
    def delete_list(self, filename):
        if not filename or filename in ["<Select File>", "<No Custom Files>"]:
            return ("❌ Error: Please select or input filename", self.get_file_list_string())
        file_path = self.get_file_path(filename)
        if not os.path.exists(file_path):
            return (f"❌ Error: File not found: {os.path.basename(file_path)}", self.get_file_list_string())
        os.remove(file_path)
        return (f"🗑️ Deleted: {os.path.basename(file_path)}", self.get_file_list_string())
    
    def get_file_list_string(self):
        files = self.get_custom_files()
        if not files:
            return "📁 Custom folder: (empty)\n\nTip: Use '📝 Create New List' to create your first custom list"
        file_list = "📁 Files in Custom folder:\n" + "=" * 50 + "\n"
        for i, filename in enumerate(files, 1):
            file_path = os.path.join(self.custom_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line for line in f.read().split('\n') if line.strip()]
                    line_count = len(lines)
                file_list += f"{i}. {filename} ({line_count} lines)\n"
            except:
                file_list += f"{i}. {filename}\n"
        return file_list


NODE_CLASS_MAPPINGS = {
    "CustomListManager": CustomListManager
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomListManager": "Custom List Manager 📝"
}

