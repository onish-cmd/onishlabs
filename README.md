Vibe Code Suite
===================

**Vibe Code Suite is a python program that slices out functions with the `ast` library provided by python and sends them to Gemini to surgically refractor code based on the users prompt. It gives the sliced function to Gemini saving tokens and prevent the AI from forgetting the context of your code.**

----------------
  Requirements
----------------

* **Python 3.9+** (Required for `ast.unparse`)
* **Libraries:** `pip install textual requests`
* **API Access:** A valid Google Gemini API Key.

---------
  Usage
---------

1. Start `main.py` with `python3 main.py` (assuming python is installed).
2. Select the file from the directory tree (file has to be in a subdirectory or same directory as the `main.py`).
3. Enter the prompt, focus function (the function to slice in the code (Classes aren't supported but functions inside classes are supported)) and your Gemini API key.
4. Click `Vibe!`
It will save the file to `ai-output.py`.
