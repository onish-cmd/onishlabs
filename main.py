"""<Vibe Code Suite, this program uses ast to slice out functions and give them to Gemini>
Copyright (C) 2026  Onish

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>."""

import ast
import requests
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, TextArea, Button, RichLog, Static
from textual.containers import Vertical, Horizontal
from textual.widgets import DirectoryTree


class TextualApp(App):
    CSS = """
    #main_screen {
    /* 1. Parent MUST have a defined height to know when children overflow */
    height: 100%;
    layout: vertical;
    overflow-y: auto; 
}

    #viewer_container {
        width: 100%;
        height: auto; 
    }
    #main_screen {
        align: center top;
        height: 100%;
    }
    Vertical {
        width: 100%;
        overflow-y: auto;
    }
    #tree {
        height: 100%; /* Important: Fill the Horizontal container's height */
        border: solid green;
    }

    #code_view {
        height: 100%; /* Important: Fill the Horizontal container's height */
        border: solid blue;
    }
    
    #tree, #code_view {
        margin: 1;
        height: 20;
        min-height: 20;
    }

    #output {
        height: auto;
        margin: 1;
        max-height: 10;
        overflow-y: scroll;
    }
    #Vibe_Button {
        /* This uses the 'primary' blue from Textual's theme */
        background: $primary; 
        color: auto;
        margin: 1;
        width: 100%;
    }
    #disclaimer {
        background: $warning-muted;
        color: $text;
        padding: 0 1;
        margin: 1 0;
        text-style: italic;
        border: round $warning;
    }

    #foss_footer {
        color: $text-primary;
        text-align: center;
        text-style: bold;
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        # New Theme added by Textual devs + my fav!
        yield Header()
        yield Vertical(
            Input(placeholder="Enter the prompt...", id="prompt"),
            Input(placeholder="Focus Function...", id="focus_func"),
            Input(
                placeholder="Enter your Groq API key...", id="api_key", password=True
            ),
            Static(
                "AI can make mistakes, always double check.",
                id="disclaimer",
            ),
            Button(label="Vibe!", id="Vibe_Button"),
            RichLog(id="output", highlight=True),
            Horizontal(
                DirectoryTree("./", id="tree"),
                TextArea(id="code_view", read_only=True),
                id="viewer_container",
            ),
            Static("For FOSS United Hackathon 2026", id="foss_footer"),
            id="main_screen",
        )
        yield Footer()

    @on(Button.Pressed, "#Vibe_Button")
    def handle_click(self):
        if not hasattr(self, "current_filename") or self.current_filename is None:
            self.notify(
                "Error: Please select a file from the tree first!", severity="error"
            )
            return
        prompt: str = self.query_one("#prompt", Input).value
        api_key = self.query_one("#api_key", Input).value
        focus_func = self.query_one("#focus_func", Input).value
        if not prompt or not api_key or not focus_func:
            self.notify(
                "Error: Fill in the Prompt, API Key, and Function Name!",
                severity="error",
            )
            return
        btn = self.query_one("#Vibe_Button", Button)
        btn.disabled = True
        btn.label = "Vibing..."
        self.notify(f"About to vibe with prompt: {prompt}")
        self.run_worker(
            lambda: build_vibe_suite(
                self.current_filename, focus_func, api_key, prompt, self
            ),
            thread=True,
            exclusive=True,
        )

    @on(DirectoryTree.FileSelected)
    def read_file(self, event: DirectoryTree.FileSelected):
        file = event.path
        self.current_filename = file
        content = file.read_text()
        code_view = self.query_one("#code_view", TextArea)
        code_view.text = content

    def reset_vibe_button(self):
        btn = self.query_one("#Vibe_Button", Button)
        btn.disabled = False
        btn.label = "Vibe!"

    def on_mount(self):
        self.theme = "tokyo-night"


# REFACTOR: This function currently mixes logic (AST) with UI (print/input).
def build_vibe_suite(filename, focus_func, API_KEY, prompt, app: App):
    app.call_from_thread(app.query_one("#output", RichLog).clear)
    with open(filename, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    function_data = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            code = ast.get_source_segment(source, node)
            if code is None:
                return ValueError("Error")
            function_data[node.name] = {"node": node, "code": code}

    to_scan = [focus_func]
    seen = set()
    collected_code = []

    for name in to_scan:
        if name in function_data and name not in seen:
            seen.add(name)
            collected_code.append(function_data[name]["code"])

            calls = [
                n.func.id
                for n in ast.walk(function_data[name]["node"])
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            ]
            to_scan.extend(calls)
    if focus_func not in function_data:
        app.call_from_thread(
            app.notify,
            f"Error: Function '{focus_func}' not found in {filename.name}",
            severity="error",
        )
        app.call_from_thread(callback=getattr(app, "reset_vibe_button"))
        return

    prompt_code = "\n\n".join(collected_code)
    app.call_from_thread(
        app.query_one("#output", RichLog).write, f"--COLLECTED CODE--\n{prompt_code}"
    )

    # --- TUI REPLACEMENT POINT 1 ---
    # Instead of print(), display prompt_code in a Textual Static or TextArea widget.
    # Replace the input() call with a Textual Input widget and a 'Vibe' Button.

    # --- END REPLACEMENT ---

    final_prompt = f"Code: {prompt_code}\n\n Prompt: {prompt}"
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {
                "role": "system",
                "content": """DO NOT USE COMMENTS, PYTHON ONLY. 
Always output the full function body. 
Never assume something is imported always import everything you need.""",
            },
            {"role": "user", "content": final_prompt},
        ],
        "temperature": 0.6,
    }

    # --- TUI REPLACEMENT POINT 2 ---
    # Instead of print("Vibing!"), trigger a Textual LoadingIndicator or update a RichLog.
    # Run the requests.post below inside a Textual @work thread to prevent UI freezing.
    try:
        data = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        ).json()
    except Exception as e:
        app.call_from_thread(app.notify, f"Failed to call Groq. Error: {e}")
        app.call_from_thread(getattr(app, "reset_vibe_button"))
        return

    # --- END REPLACEMENT ---

    try:
        raw_text = data["choices"][0]["message"]["content"]
        ai_code = raw_text.replace("```python", "").replace("```", "").strip()

        # Parse the AI's code into its own mini-tree
        ai_tree = ast.parse(ai_code)

        # 3. The "In-Place" Replacement
        class FunctionReplacer(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == focus_func:
                    # We found the function!
                    # We replace the original node with the AI's version
                    # Assuming the AI returned a FunctionDef
                    for new_node in ai_tree.body:
                        if (
                            isinstance(new_node, ast.FunctionDef)
                            and new_node.name == focus_func
                        ):
                            return ast.copy_location(new_node, node)
                    else:
                        raise ValueError("Function not found in AI code!!!")
                return node

        # Transform the full file tree
        modified_tree = FunctionReplacer().visit(tree)
        ast.fix_missing_locations(modified_tree)

        # 4. Generate the whole file back as a string
        # This automatically handles all indentation for the entire file!
        final_source = ast.unparse(modified_tree)
        app.call_from_thread(
            app.query_one("#output", RichLog).write, f"--AI CODE--\n{final_source}"
        )

        with open("ai-output.py", "w") as f:
            f.write(final_source)

        app.call_from_thread(app.notify, "Whole file updated successfully! Saved!")
        app.call_from_thread(getattr(app, "reset_vibe_button"))

        # --- TUI REPLACEMENT POINT 3 ---
        # Instead of print("Done Vibing!"), show a Textual Toast (self.notify) or a success Screen.

    except Exception as e:
        # Instead of dumping JSON to stdout, log the error to a Textual RichLog.
        app.call_from_thread(app.notify, f"Error: {e}")
        try:
            message = data["error"]["message"]
        except Exception:
            message = e
        app.call_from_thread(app.notify, f"DEBUG: {message} JSON in output.")
        app.call_from_thread(
            app.query_one("#output", RichLog).write, f"--JSON--\n{data}"
        )
        app.call_from_thread(getattr(app, "reset_vibe_button"))


def main():
    app = TextualApp()
    app.run()


main()
