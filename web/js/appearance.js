import { app } from "/scripts/app.js";

const COLOR_THEMES = {
    promptor: {nodeColor: "#1c2b23", nodeBgColor: "#3a5949", width: 300},
    ai: {nodeColor: "#0a67cc", nodeBgColor: "#264468", width: 360},
    tools: {nodeColor: "#3a464c", nodeBgColor: "#263238", width: 330},

};

const NODE_COLORS = {
    // promptor nodes
    "PromptConcat": "promptor",
    "PromptBuilder": "promptor",
    "KeywordPicker": "promptor",
    "WildPromptor_AllInOne": "promptor",
    "WildPromptor_DataToPromptList": "promptor",
    "WildPromptor_Generator": "promptor",
    "WildPromptor_AllInOneList": "promptor",

    // ai nodes
    "WildPromptor_Enhancer": "ai",
    "WildPromptor_GeminiVision": "ai",
    "WildPromptor_Qwen": "ai",
    "WildPromptor_hfgpt": "ai",
    "WildPromptor_minicpm": "ai",
    "WildPromptor_Ollama": "ai",
    "WildPromptor_LLMAPI": "ai",
    "wildpromptor_JanusPro": "ai",
    "WildPromptor_BLIP": "ai",
    "WildPromptor_hfgpt": "ai",

    // prompt Tools
    "PromptCleaner": "tools",
    "AIOutputCleaner": "tools",
    "WildPromptor_ShowPrompt": "tools",
    "WildPromptor_TextInput": "tools",
};

function setNodeColors(node, theme) {
    if (!theme) { return; }
    if (theme.nodeColor) {
        node.color = theme.nodeColor;
    }
    if (theme.nodeBgColor) {
        node.bgcolor = theme.nodeBgColor;
    }
    if (theme.width) {
        node.size = node.size || [140, 80];
        node.size[0] = theme.width;
    }
}

const ext = {
    name: "Wildpromtor.appearance",

    nodeCreated(node) {
        const nclass = node.comfyClass;
        if (NODE_COLORS.hasOwnProperty(nclass)) {
            let colorKey = NODE_COLORS[nclass];
            const theme = COLOR_THEMES[colorKey];
            setNodeColors(node, theme);
        }
    }
};

app.registerExtension(ext);