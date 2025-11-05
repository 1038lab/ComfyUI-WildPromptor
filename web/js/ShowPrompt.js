import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
    name: "WildPromptor.WildPromptor_ShowPrompt",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        
        // --- FIX 1 ---
        // Check for the correct node name from NODE_CLASS_MAPPINGS
        // Was: if (nodeData.name === "Show_String") {
        if (nodeData.name === "WildPromptor_ShowPrompt") {
            
            function renderString(text) {
                if (this.widgets) {
                    let keep = this.inputs?.[0]?.widget ? 1 : 0;
                    while (this.widgets.length > keep) {
                        this.widgets.pop().onRemove?.();
                    }
                }
                
                // This correctly handles the list from Python
                let lines = Array.isArray(text) ? text : [text];
                
                for (let t of lines) {
                    let widget = ComfyWidgets["STRING"](
                        this,
                        "show_" + (this.widgets?.length ?? 0),
                        ["STRING", { multiline: true }],
                        app
                    ).widget;
                    widget.inputEl.readOnly = true;
                    widget.inputEl.style.opacity = 0.7;
                    widget.value = t; // t will be a string, e.g., "my generated prompt"
                }
                
                // Resize node to fit content
                setTimeout(() => {
                    let size = this.computeSize();
                    if (size[0] < this.size[0]) size[0] = this.size[0];
                    if (size[1] < this.size[1]) size[1] = this.size[1];
                    this.onResize?.(size);
                    app.graph.setDirtyCanvas(true, false);
                }, 0);
            }

            // `onExecuted` is called when the node finishes running
            nodeType.prototype.onExecuted = function (msg) {
                // --- FIX 2 ---
                // The data is in `msg.prompt`, based on the Python return
                // Was: renderString.call(this, msg.text);
                if (msg.prompt) {
                    renderString.call(this, msg.prompt);
                }
            };

            // This logic handles re-loading the prompt from saved workflow/png info
            const WIDGETS_CACHE = Symbol();
            const oldConfigure = nodeType.prototype.configure;
            nodeType.prototype.configure = function () {
                this[WIDGETS_CACHE] = arguments[0]?.widgets_values;
                return oldConfigure?.apply(this, arguments);
            };
            
            const oldOnConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function () {
                oldOnConfigure?.apply(this, arguments);
                let values = this[WIDGETS_CACHE];
                if (values?.length) {
                    setTimeout(() => {
                        // This logic seems fine, it avoids re-displaying an input widget
                        renderString.call(this, values.slice(+(values.length > 1 && this.inputs?.[0]?.widget)));
                    }, 0);
                }
            };
        }
    },
});