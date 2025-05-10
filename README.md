# 🚀 cutieAPI - Your Friendly Command-Line API Client 🚀

cutieAPI is a Python-based, interactive command-line tool designed to make API testing and interaction easy and enjoyable, right from your terminal! It's built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output and `requests` for robust HTTP communication.

Think of it as a lightweight, terminal-first companion for your API development workflow, similar in spirit to tools like Postman or Insomnia, but living entirely in your console.

## 🎬 Demo

![Demo](cutieApi.jpg)

## ✨ Features

*   **Interactive Request Building:** Guided prompts for every step.
*   **Multiple Body Types:** JSON, Form Data, Raw Text, and File Uploads.
*   **Pretty Output:** Colorized, formatted, and syntax-highlighted responses.
*   **Request History:** Quickly re-run past requests.
*   **Saved Requests:** Store and load complex request configurations.
*   **Environment Variables:** Use placeholders like `{{base_url}}` for dynamic values.
*   **Bearer Token Helper:** Easy `Authorization: Bearer <token>` header management.
*   **Save Response to File:** Download API responses.
*   **Cross-Platform:** Works on Linux, macOS, and Windows.

## 🛠️ Installation

1.  **Prerequisites:**
    *   Python 3.8+
    *   `pip` (Python package installer)

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/samunderSingh12/cutieAPI.git
    cd cutieAPI
    ```

3.  **Install Dependencies:**
    cutieAPI relies on `requests` and `rich`.
    ```bash
    pip install requests rich
    ```
    *(Recommended: Use a virtual environment)*
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install requests rich
    ```

## 🚀 How to Use

1.  **Run cutieAPI:**
    Navigate to the directory containing `main.py` and run:
    ```bash
    python main.py
    ```
    You'll be greeted with the main menu:
    ```
    ╭───────────────────────────────────────────╮
    │ 🚀 cutieAPI vX.X.X 🚀 - Enhanced Edition │
    ╰───────────────────────────────────────────╯
    ───────────────────────── Configure New Request ──────────────────────────
    Start with? [new/history/load/env/quit] (new):
    ```

2.  **Initial Action - Choose Your Starting Point:**
    *   **`new` (Default):** Start building a request from scratch.
    *   **`history`:** View past requests.
        ```
        Request History
        ┏━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ # ┃ Timestamp  ┃ Method ┃ URL                          ┃
        ┡━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
        │ 1 │ 2023-10-27 │ POST   │ http://localhost:8000/items/ │
        │ 2 │ 2023-10-27 │ GET    │ http://localhost:8000/ping   │
        └─ Rerun Request ───────────────┘
        Enter # to re-run (0 to cancel) (0): 1
        ```
    *   **`load`:** Load a previously saved request configuration.
        ```
        Saved Requests
        ┏━━━┳━━━━━━━━━━━━━━━━━━━━━┓
        ┃ # ┃ Request Name        ┃
        ┡━━━╇━━━━━━━━━━━━━━━━━━━━━┩
        │ 1 │ create_new_user     │
        │ 2 │ get_all_products    │
        └─ Load Request ───────────────┘
        Enter # to load (0 to cancel) (0): 1
        ```
    *   **`env`:** Manage environment variables. You can add, remove, or list variables like `{{base_url}}` or `{{auth_token}}`.
        ```
        Action? [add/remove/list/done] (done): add
        Variable name (e.g., base_url): api_key
        Value for api_key: your_secret_api_key_here
        ```
    *   **`quit`:** Exit cutieAPI.

3.  **Define the Request Method & URL:**
    ```
    Enter HTTP method [GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS] (GET): POST
    Enter the full API URL (e.g., {{base_url}}/items): {{base_url}}/items
    ```
    *(cutieAPI will substitute `{{base_url}}` if you've defined it in `env`)*

4.  **Add Query Parameters (Optional):**
    ```
    Manage query parameters? (y/N) [False]: y
    Current query parameters: None
    Enter query parameters one by one (e.g., limit=10)... Empty line to finish.
    Query Param (key=value, or empty to finish): page=1
    Query Param (key=value, or empty to finish): limit=20
    Query Param (key=value, or empty to finish):
    ```

5.  **Manage Headers (Optional):**
    ```
    Manage custom headers? (y/N) [False]: y
    Current headers: None
    Enter headers one by one... Empty line to finish.
    Header (or leave empty to finish): Content-Type: application/json
    Header (or leave empty to finish): X-Custom-Header: MyValue
    Header (or leave empty to finish):
    ```
    *   **Bearer Token Helper:**
        ```
        Add/Update Bearer Token Authorization? (y/N) [False]: y
        Enter Bearer Token: your_jwt_token_here
        ```

6.  **Specify Request Body (for `POST`, `PUT`, `PATCH`):**
    You'll be prompted for the `Request body type?`.

    *   **`json`**:
        ```
        Request body type? [json/form/file/raw/none] (json): json
        Enter JSON body. Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to finish.
        {
          "name": "cutieAPI Test",
          "value": 123,
          "tags": ["test", "{{env_tag}}"]
        }
        <Ctrl+D>
        ```
    *   **`form`** (`application/x-www-form-urlencoded`):
        ```
        Request body type? [json/form/file/raw/none] (json): form
        Enter form data (key=value, one per line)... Empty line to finish.
        Form data (key=value, or empty to finish): username=cutie
        Form data (key=value, or empty to finish): type=api
        Form data (key=value, or empty to finish):
        ```
    *   **`file`** (`multipart/form-data`):
        ```
        Request body type? [json/form/file/raw/none] (json): file
        Enter text fields for multipart form (key=value)... Empty line to finish.
        Text field (key=value, or empty to finish): description=Test upload
        Text field (key=value, or empty to finish):
        Add files for multipart form.
        Add/Update a file? (Y/n) [True]: y
        Form field name for the file (e.g., 'upload_file'): myFile
        Path to the file: /path/to/your/document.pdf
        ```
    *   **`raw`**:
        ```
        Request body type? [json/form/file/raw/none] (json): raw
        Enter raw text body. Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to finish.
        <xml><message>Hello from cutieAPI!</message></xml>
        <Ctrl+D>
        ```
    *   **`none`**: No request body will be sent.

7.  **Review Sent Request & View Response:**
    cutieAPI will display a summary of what's being sent, then the server's response:
    ```
    ────────────────── Sending POST request to http://localhost:8000/items ───────────────────
    Query Params: {'page': '1', 'limit': '20'}

    Headers Sent:
      Content-Type: application/json
      X-Custom-Header: MyValue

    JSON Body Sent:
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ 1 {                                                                          ┃
    ┃ 2   "name": "cutieAPI Test",                                                 ┃
    ┃ 3   "value": 123,                                                           ┃
    ┃ 4   "tags": [                                                                ┃
    ┃ 5     "test",                                                                ┃
    ┃ 6     "beta"                                                                 ┃
    ┃ 7   ]                                                                        ┃
    ┃ 8 }                                                                          ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    ───────────────────────── Response Received (15.32 ms) ─────────────────────────
    Status Code: 201 Created

    Response Headers:
    ┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ date               ┃ Fri, 27 Oct 2023 10:00:00 GMT                         ┃
    ┃ server             ┃ uvicorn                                               ┃
    ┃ content-type       ┃ application/json                                      ┃
    ┗━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    Response Body:
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ 1 {                                                                          ┃
    ┃ 2   "id": 101,                                                               ┃
    ┃ 3   "name": "cutieAPI Test",                                                 ┃
    ┃ 4   "value": 123,                                                           ┃
    ┃ 5   "tags": [                                                                ┃
    ┃ 6     "test",                                                                ┃
    ┃ 7     "beta"                                                                 ┃
    ┃ 8   ],                                                                       ┃
    ┃ 9   "message": "Item created successfully"                                   ┃
    ┃10 }                                                                          ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    ```

8.  **Post-Request Actions:**
    *   **Save Response Body?**: Prompts you to save the response content to a local file.
    *   **Save this request configuration?**: Allows you to save the entire request setup (URL, headers, body, etc.) for quick loading later.
    *   **Make another request?**: Choose to continue or exit cutieAPI.

## 💾 Data Storage

*   **History:** `~/.api_buddy_history.json` (stores last 50 requests).
    *   _Note: The filename still uses `api_buddy`. You might want to update this in the code (`HISTORY_FILE` variable) to `~/.cutieapi_history.json` for consistency if you haven't already._
*   **Saved Requests:** `~/.api_buddy_saved_requests/`
    *   _Note: Similarly, consider renaming this directory in code (`SAVED_REQUESTS_DIR` variable) to `~/.cutieapi_saved_requests/`._

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes and test them thoroughly.
4.  Commit your changes (`git commit -am 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Create a new Pull Request.

If you encounter any bugs or have feature suggestions, please open an issue on GitHub.

## 📜 License

This project is open-source and available under the [MIT License](LICENSE.md)

---

Happy API Bashing with cutieAPI! 🎉
