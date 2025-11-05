import { app } from "/scripts/app.js";

app.registerExtension({
    name: "WildPromptor.OllamaNode",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "WildPromptorOllamaVision") {
            const originalNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = async function () {
                if (originalNodeCreated) {
                    originalNodeCreated.apply(this, arguments);
                }

                const serverUrlWidget = this.widgets.find((w) => w.name === "server_url");
                const modelWidget = this.widgets.find((w) => w.name === "model");

                const fetchModels = async (url) => {
                    try {
                        const serverUrl = url && url.trim() ? url.trim() : "http://localhost:11434";
                        
                        const response = await fetch("/ollama/get_models", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({
                                url: serverUrl,
                            }),
                        });

                        if (response.ok) {
                            const models = await response.json();
                            console.debug("Fetched models:", models);
                            return models;
                        } else {
                            console.error(`Failed to fetch models: ${response.status}`);
                            return [];
                        }
                    } catch (error) {
                        console.error(`Error fetching models`, error);
                        return [];
                    }
                };

                const updateModels = async () => {
                    let url = serverUrlWidget.value;
                    if (!url || !url.trim()) {
                        url = "http://localhost:11434";
                        serverUrlWidget.value = url;
                    }
                    
                    const prevValue = modelWidget.value;
                    modelWidget.value = '';
                    modelWidget.options.values = [];

                    const models = await fetchModels(url);

                    modelWidget.options.values = models;
                    console.debug("Updated modelWidget.options.values:", modelWidget.options.values);

                    if (models.includes(prevValue)) {
                        modelWidget.value = prevValue;
                    } else if (models.length > 0) {
                        modelWidget.value = models[0];
                    }

                    console.debug("Updated modelWidget.value:", modelWidget.value);
                };

                serverUrlWidget.callback = updateModels;

                const dummy = async () => {
                };

                await dummy();
                await updateModels();
            };
        }
    },
}); 