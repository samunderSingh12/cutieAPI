import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.text import Text
from rich.padding import Padding
from rich.pretty import pprint

console = Console()
HISTORY_FILE = Path.home() / ".api_buddy_history.json"
SAVED_REQUESTS_DIR = Path.home() / ".api_buddy_saved_requests"
SAVED_REQUESTS_DIR.mkdir(parents=True, exist_ok=True)

request_history = []
environment_vars = {
    "base_url": "http://localhost:8000" # Example default
}

def load_history():
    global request_history
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                request_history = json.load(f)
        except json.JSONDecodeError:
            console.print("[yellow]Warning: History file is corrupted. Starting fresh.[/yellow]")
            request_history = []
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load history: {e}[/yellow]")
            request_history = []

def save_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(request_history, f, indent=2)
    except Exception as e:
        console.print(f"[red]Error saving history: {e}[/red]")

def add_to_history(method, url, headers, data_payload, json_payload, files_info_for_history):
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "method": method,
        "url": url,
        "headers": headers,
        "data_payload": data_payload,
        "json_payload": json_payload,
        "files_info": files_info_for_history
    }
    request_history.insert(0, history_entry)
    if len(request_history) > 50:
        request_history.pop()
    save_history()

def show_history_and_select():
    if not request_history:
        console.print("No history yet.")
        return None

    table = Table(title="Request History")
    table.add_column("#", style="dim", width=3)
    table.add_column("Timestamp", style="magenta")
    table.add_column("Method", style="green")
    table.add_column("URL")

    for i, entry in enumerate(request_history):
        table.add_row(str(i + 1), entry["timestamp"].split("T")[0], entry["method"], entry["url"])

    choice = IntPrompt.ask("Enter # to re-run (0 to cancel)", default=0, choices=[str(i) for i in range(len(request_history) + 1)])

    if 0 < choice <= len(request_history):
        selected_entry = request_history[choice - 1]
        console.print(f"Re-running: [bold cyan]{selected_entry['method']} {selected_entry['url']}[/bold cyan]")
        if selected_entry.get("files_info"):
            console.print("[yellow]Warning: This request involved files. File paths may need to be re-entered.[/yellow]")
        return selected_entry
    return None

def save_request_to_file(method, url, headers, data_payload, json_payload, files_info_for_saving, query_params):
    request_name = Prompt.ask("Enter a name for this request (e.g., create_user_prod)").strip().replace(" ", "_")
    if not request_name:
        console.print("[yellow]Save cancelled: No name provided.[/yellow]")
        return

    request_data = {
        "method": method,
        "url": url,
        "headers": headers,
        "query_params": query_params,
        "data_payload": data_payload,
        "json_payload": json_payload,
        "files_info": files_info_for_saving
    }
    filepath = SAVED_REQUESTS_DIR / f"{request_name}.json"
    try:
        with open(filepath, "w") as f:
            json.dump(request_data, f, indent=2)
        console.print(f"[green]Request '{request_name}' saved to {filepath}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving request: {e}[/red]")

def load_request_from_file():
    saved_files = [f.name for f in SAVED_REQUESTS_DIR.glob("*.json")]
    if not saved_files:
        console.print("No saved requests found.")
        return None

    table = Table(title="Saved Requests")
    table.add_column("#", style="dim", width=3)
    table.add_column("Request Name", style="cyan")

    for i, filename in enumerate(saved_files):
        table.add_row(str(i + 1), filename.replace(".json", ""))
    console.print(table)

    choice = IntPrompt.ask("Enter # to load (0 to cancel)", default=0, choices=[str(i) for i in range(len(saved_files) + 1)])

    if 0 < choice <= len(saved_files):
        filepath = SAVED_REQUESTS_DIR / saved_files[choice - 1]
        try:
            with open(filepath, "r") as f:
                loaded_data = json.load(f)
                console.print(f"Loaded request: [bold cyan]{loaded_data['method']} {loaded_data['url']}[/bold cyan]")
                if loaded_data.get("files_info"):
                    console.print("[yellow]Warning: This saved request involved files. You may need to re-select them.[/yellow]")
                return loaded_data
        except Exception as e:
            console.print(f"[red]Error loading request: {e}[/red]")
    return None

def substitute_env_vars(value):
    if not isinstance(value, str):
        return value
    for key, var_val in environment_vars.items():
        value = value.replace(f"{{{{{key}}}}}", str(var_val))
    return value

def manage_env_vars():
    global environment_vars
    console.rule("[bold cyan]Environment Variables[/bold cyan]")
    if not environment_vars:
        console.print("No environment variables set.")
    else:
        table = Table("Variable", "Value")
        for key, val in environment_vars.items():
            table.add_row(key, str(val))
        console.print(table)

    action = Prompt.ask("Action? (add, remove, list, done)", choices=["add", "remove", "list", "done"], default="done")
    if action == "add":
        key = Prompt.ask("Variable name (e.g., base_url)")
        value = Prompt.ask(f"Value for {key}")
        environment_vars[key] = value
        console.print(f"[green]Variable '{key}' set.[/green]")
    elif action == "remove":
        key = Prompt.ask("Variable name to remove")
        if key in environment_vars:
            del environment_vars[key]
            console.print(f"[green]Variable '{key}' removed.[/green]")
        else:
            console.print(f"[yellow]Variable '{key}' not found.[/yellow]")
    elif action == "list":
        if not environment_vars:
            console.print("No environment variables set.")
        else:
            table = Table("Variable", "Value")
            for key, val in environment_vars.items():
                table.add_row(key, str(val))
            console.print(table)
    if action != "done":
        manage_env_vars()

def get_user_input(prefill_data=None):
    console.rule("[bold blue]Configure New Request[/bold blue]")

    if not prefill_data:
        action = Prompt.ask(
            "Start with?",
            choices=["new", "history", "load", "env", "quit"],
            default="new",
            case_sensitive=False
        )
        if action == "quit":
            return "quit"
        if action == "history":
            prefill_data = show_history_and_select()
            if not prefill_data: return None
        elif action == "load":
            prefill_data = load_request_from_file()
            if not prefill_data: return None
        elif action == "env":
            manage_env_vars()
            return get_user_input()

    method_choices = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    default_method = prefill_data.get("method", "GET") if prefill_data else "GET"
    method = Prompt.ask(
        "Enter HTTP method",
        choices=method_choices,
        default=default_method,
        case_sensitive=False
    ).upper()

    default_url = substitute_env_vars(prefill_data.get("url", "")) if prefill_data else ""
    url_prompt_text = "Enter the full API URL (e.g., {{base_url}}/items)"
    url = Prompt.ask(url_prompt_text)
    url = substitute_env_vars(url)

    re_prompt_default_url = substitute_env_vars(prefill_data.get("url", "")) if prefill_data else ""
    while not (url.startswith("http://") or url.startswith("https://")):
        console.print("[bold red]Invalid URL. Must start with 'http://' or 'https://'.[/bold red]")
        url = Prompt.ask("Enter the full API URL", default=re_prompt_default_url)
        url = substitute_env_vars(url)

    query_params = prefill_data.get("query_params", {}) if prefill_data else {}
    if Confirm.ask("Manage query parameters?", default=bool(query_params)):
        console.print("Current query parameters:", query_params if query_params else "None")
        console.print("Enter query parameters one by one (e.g., limit=10). Prefix with '-' to remove (e.g., -limit). Empty line to finish.")
        while True:
            qp_input = Prompt.ask("Query Param (key=value, or empty to finish)").strip()
            if not qp_input: break
            if qp_input.startswith("-"):
                key_to_remove = qp_input[1:].strip()
                if key_to_remove in query_params:
                    del query_params[key_to_remove]
                    console.print(f"[yellow]Removed query param: {key_to_remove}[/yellow]")
                else:
                    console.print(f"[yellow]Query param '{key_to_remove}' not found.[/yellow]")
                continue
            if "=" not in qp_input:
                console.print("[yellow]Warning: Query param should be 'key=value'. Skipping.[/yellow]"); continue
            key, value = qp_input.split("=", 1)
            query_params[key.strip()] = substitute_env_vars(value.strip())

    headers = prefill_data.get("headers", {}) if prefill_data else {}
    if Confirm.ask("Manage custom headers?", default=bool(headers)):
        console.print("Current headers:")
        if headers:
            for k, v in headers.items(): console.print(f"  {k}: {v}")
        else:
            console.print("  None")
        console.print("Enter headers one by one (e.g., Authorization: Bearer token). Prefix with '-' to remove (e.g., -Content-Type). Press Enter on an empty line to finish.")
        while True:
            header_input = Prompt.ask("Header (or leave empty to finish)").strip()
            if not header_input: break
            if header_input.startswith("-"):
                key_to_remove = header_input[1:].strip()
                found_key = next((k for k in headers if k.lower() == key_to_remove.lower()), None)
                if found_key:
                    del headers[found_key]
                    console.print(f"[yellow]Removed header: {found_key}[/yellow]")
                else:
                    console.print(f"[yellow]Header '{key_to_remove}' not found to remove.[/yellow]")
                continue
            if ":" not in header_input:
                console.print("[yellow]Warning: Header should be in 'Key: Value' format. Skipping.[/yellow]"); continue
            key, value = header_input.split(":", 1)
            headers[key.strip()] = substitute_env_vars(value.strip())

    if Confirm.ask("Add/Update Bearer Token Authorization?", default=False):
        token = Prompt.ask("Enter Bearer Token")
        headers["Authorization"] = f"Bearer {substitute_env_vars(token)}"
        console.print("[green]Authorization header set/updated.[/green]")

    data_payload = prefill_data.get("data_payload") if prefill_data else None
    json_payload = prefill_data.get("json_payload") if prefill_data else None
    files_to_send = {}
    prefilled_files_info = prefill_data.get("files_info") if prefill_data else None


    if method in ["POST", "PUT", "PATCH"]:
        body_choices = ["json", "form", "file", "raw", "none"]
        default_body_type = "none"
        ct_header = next((v for k, v in headers.items() if k.lower() == 'content-type'), "").lower()
        if prefill_data:
            if prefill_data.get("json_payload") is not None: default_body_type = "json"
            elif prefill_data.get("files_info") is not None: default_body_type = "file"
            elif prefill_data.get("data_payload") is not None:
                if isinstance(prefill_data.get("data_payload"), dict): default_body_type = "form"
                elif isinstance(prefill_data.get("data_payload"), str): default_body_type = "raw"
        elif 'application/json' in ct_header: default_body_type = "json"
        elif 'multipart/form-data' in ct_header: default_body_type = "file"
        elif 'application/x-www-form-urlencoded' in ct_header: default_body_type = "form"

        body_type = Prompt.ask("Request body type?", choices=body_choices, default=default_body_type).lower()

        if body_type == "json":
            current_json = prefill_data.get("json_payload") if prefill_data else None
            if current_json:
                console.print(Panel(json.dumps(current_json, indent=2), title="Current JSON (edit below or paste new)"))
            console.print("Enter JSON body. Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to finish.")
            json_lines = [];
            try:
                while True: json_lines.append(input())
            except EOFError: pass
            json_string = "\n".join(json_lines)
            if json_string.strip():
                try:
                    json_payload = json.loads(json_string)
                    if not any(k.lower() == 'content-type' for k in headers.keys()):
                        headers['Content-Type'] = 'application/json'
                except json.JSONDecodeError as e:
                    console.print(f"[bold red]Invalid JSON input: {e}[/bold red]"); return None
            elif current_json:
                json_payload = current_json
                if not any(k.lower() == 'content-type' for k in headers.keys()):
                    headers['Content-Type'] = 'application/json'
            else: json_payload = None
            data_payload = None

        elif body_type == "form":
            data_payload = prefill_data.get("data_payload") if prefill_data and isinstance(prefill_data.get("data_payload"), dict) else {}
            console.print("Enter form data (key=value, one per line). Empty line to finish.")
            if data_payload: console.print("Current form data:", data_payload)
            while True:
                entry = Prompt.ask("Form data (key=value, or empty to finish)").strip()
                if not entry: break
                if "=" not in entry: console.print("[yellow]Warning: Form data should be 'key=value'. Skipping.[/yellow]"); continue
                key, value = entry.split("=", 1); data_payload[key.strip()] = substitute_env_vars(value.strip())
            if not any(k.lower() == 'content-type' for k in headers.keys()) and data_payload:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
            json_payload = None

        elif body_type == "file":
            if any(k.lower() == 'content-type' for k in headers.keys()):
                console.print("[yellow]Content-Type header will be set by 'requests' for multipart/form-data. User-set Content-Type ignored.[/yellow]")
                headers = {k:v for k,v in headers.items() if k.lower() != 'content-type'}
            data_payload = prefill_data.get("data_payload") if prefill_data and isinstance(prefill_data.get("data_payload"), dict) else {}
            console.print("Enter text fields for multipart form (key=value). Empty line to finish.")
            if data_payload: console.print("Current text fields:", data_payload)
            while True:
                entry = Prompt.ask("Text field (key=value, or empty to finish)").strip()
                if not entry: break
                if "=" not in entry: console.print("[yellow]Warning: Text field should be 'key=value'. Skipping.[/yellow]"); continue
                key, value = entry.split("=", 1); data_payload[key.strip()] = substitute_env_vars(value.strip())

            console.print("Add files for multipart form.")
            if prefilled_files_info:
                 console.print("[cyan]Prefilled file info (paths may need verification):[/cyan]", prefilled_files_info)

            while Confirm.ask("Add/Update a file?", default=True):
                form_field_name = Prompt.ask("Form field name for the file (e.g., 'upload_file')")
                default_path = prefilled_files_info.get(form_field_name, "") if prefilled_files_info else ""
                file_path_str = Prompt.ask("Path to the file", default=default_path)
                file_path = Path(substitute_env_vars(file_path_str))
                if file_path.is_file():
                    try:
                        files_to_send[form_field_name] = (file_path.name, open(file_path, 'rb'))
                        console.print(f"[green]Added file '{file_path.name}' for field '{form_field_name}'[/green]")
                    except Exception as e: console.print(f"[red]Could not open file {file_path}: {e}[/red]")
                else: console.print(f"[red]File not found: {file_path}[/red]")
            json_payload = None


        elif body_type == "raw":
            current_raw = prefill_data.get("data_payload") if prefill_data and isinstance(prefill_data.get("data_payload"), str) else None
            if current_raw:
                console.print(Panel(current_raw, title="Current Raw Data (edit or paste new)"))
            console.print("Enter raw text body. Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to finish.")
            raw_lines = [];
            try:
                while True: raw_lines.append(input())
            except EOFError: pass
            raw_string = "\n".join(raw_lines)
            if raw_string.strip(): data_payload = raw_string
            elif current_raw: data_payload = current_raw
            else: data_payload = None
            json_payload = None

        elif body_type == "none":
            data_payload = None
            json_payload = None

    if json_payload is not None: data_payload = None
    if files_to_send: json_payload = None

    return method, url, headers, data_payload, json_payload, files_to_send, query_params


def make_api_request(method, url, headers, data_payload, json_payload, files_to_send, query_params):
    console.rule(f"[bold blue]Sending {method} request to {url}")
    if query_params:
        processed_query_params = {k: substitute_env_vars(v) for k, v in query_params.items()}
        console.print(f"[bold]Query Params:[/bold] {processed_query_params}")
    else:
        processed_query_params = None


    if headers:
        processed_headers = {k: substitute_env_vars(v) for k,v in headers.items()}
        console.print("\n[bold]Headers Sent:[/bold]")
        for key, value in processed_headers.items():
            console.print(f"  {key}: {value}")
    else:
        processed_headers = {}


    final_json_payload = None
    final_data_payload = None
    final_files_payload = None
    multipart_text_fields = None

    def substitute_in_json(item):
        if isinstance(item, dict): return {k: substitute_in_json(v) for k, v in item.items()}
        elif isinstance(item, list): return [substitute_in_json(i) for i in item]
        elif isinstance(item, str): return substitute_env_vars(item)
        return item

    if json_payload is not None:
        final_json_payload = substitute_in_json(json_payload)
        console.print("\n[bold]JSON Body Sent:[/bold]")
        syntax = Syntax(json.dumps(final_json_payload, indent=2), "json", theme="monokai", line_numbers=True)
        console.print(syntax)
    elif files_to_send:
        final_files_payload = files_to_send
        multipart_text_fields = {k: substitute_env_vars(v) for k, v in data_payload.items()} if data_payload else None
        console.print("\n[bold]Multipart Form Data Sent:[/bold]")
        if multipart_text_fields:
            for key, value in multipart_text_fields.items(): console.print(f"  [Field] {key}: {value}")
        for field_name, file_tuple in final_files_payload.items():
            console.print(f"  [File] {field_name}: {file_tuple[0]}")
    elif data_payload and isinstance(data_payload, dict):
        final_data_payload = {k: substitute_env_vars(v) for k, v in data_payload.items()}
        console.print("\n[bold]Form Data Sent:[/bold]")
        for key, value in final_data_payload.items(): console.print(f"  {key}: {value}")
    elif data_payload and isinstance(data_payload, str):
        final_data_payload = substitute_env_vars(data_payload)
        console.print("\n[bold]Raw Body Sent:[/bold]")
        console.print(Panel(final_data_payload, expand=False))


    start_time = time.monotonic()
    response = None
    history_files_info = {}
    if files_to_send:
        history_files_info = {k: (v[1].name if hasattr(v[1], 'name') and Path(v[1].name).is_file() else v[0]) for k, v in files_to_send.items()}


    try:
        response = requests.request(
            method,
            url,
            params=processed_query_params,
            headers=processed_headers,
            data=multipart_text_fields if final_files_payload else final_data_payload,
            json=final_json_payload,
            files=final_files_payload,
            timeout=30
        )
        end_time = time.monotonic()
        duration_ms = (end_time - start_time) * 1000

        console.rule(f"[bold green]Response Received ({duration_ms:.2f} ms)[/bold green]")
        console.print(f"[bold]Status Code:[/bold] {response.status_code} {response.reason}")

        console.print("\n[bold]Response Headers:[/bold]")
        header_table = Table(show_header=False, box=None)
        for key, value in response.headers.items():
            header_table.add_row(f"[cyan]{key}[/cyan]", value)
        console.print(header_table)

        console.print("\n[bold]Response Body:[/bold]")
        content_type = response.headers.get("Content-Type", "").lower()

        if response.content:
            if Confirm.ask("Save response body to file?", default=False):
                default_filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if "application/json" in content_type: default_filename += ".json"
                elif "text/html" in content_type: default_filename += ".html"
                elif "text/plain" in content_type: default_filename += ".txt"
                elif "image/jpeg" in content_type: default_filename += ".jpg"
                elif "image/png" in content_type: default_filename += ".png"
                elif "application/pdf" in content_type: default_filename += ".pdf"
                else: default_filename += ".bin"

                save_filename_str = Prompt.ask("Enter filename to save response", default=default_filename)
                save_path = Path(save_filename_str)
                try:
                    with open(save_path, "wb") as f: f.write(response.content)
                    console.print(f"[green]Response saved to {save_path.resolve()}[/green]")
                except Exception as e: console.print(f"[red]Error saving response file: {e}[/red]")

        if "application/json" in content_type:
            try:
                json_body = response.json()
                syntax = Syntax(json.dumps(json_body, indent=2), "json", theme="monokai", line_numbers=True)
                console.print(syntax)
            except json.JSONDecodeError:
                console.print(Panel(response.text, title="Raw Text (Not valid JSON)", expand=False, border_style="yellow"))
        elif "text/html" in content_type:
            syntax = Syntax(response.text, "html", theme="monokai", line_numbers=True)
            console.print(syntax)
        elif "text/" in content_type:
            console.print(Panel(response.text, title="Plain Text", expand=False))
        else:
            console.print(f"Non-text content type: {content_type}. Size: {len(response.content)} bytes.")
            if len(response.content) > 0 and Confirm.ask(f"Try to display as text?", default=False):
                try: console.print(Panel(response.text, title=f"Raw Content ({content_type})", expand=False))
                except Exception as e: console.print(f"[red]Could not display content as text: {e}[/red]")
            else:
                console.print("Skipping display of non-text response body.")


    except requests.exceptions.Timeout:
        console.print("[bold red]Error: Request timed out.[/bold red]")
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Error: Could not connect to the server. Is the URL correct and the server running?[/bold red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
    finally:
        if final_files_payload:
            for _, file_tuple in final_files_payload.items():
                if file_tuple and hasattr(file_tuple[1], 'close') and not file_tuple[1].closed:
                    file_tuple[1].close()
    console.rule()
    add_to_history(method, url, headers, data_payload, json_payload, history_files_info)


if __name__ == "__main__":
    load_history()
    console.print(Panel("🚀 cutieAPI v2 🚀", title_align="center", expand=False))

    while True:
        user_inputs_tuple = get_user_input()

        if user_inputs_tuple == "quit": break
        if not user_inputs_tuple:
            if not Confirm.ask("\nContinue to new request or quit?", default=True): break
            continue

        method, url, headers, data_payload, json_payload, files_to_send, query_params = user_inputs_tuple

        files_info_for_saving = {}
        if files_to_send:
            for field_name, (filename, file_obj) in files_to_send.items():
                original_path = file_obj.name if hasattr(file_obj, 'name') and Path(file_obj.name).is_file() else filename
                files_info_for_saving[field_name] = str(original_path)


        if Confirm.ask("\nSave this request configuration (before sending)?", default=False):
            save_request_to_file(method, url, headers, data_payload, json_payload, files_info_for_saving, query_params)


        make_api_request(method, url, headers, data_payload, json_payload, files_to_send, query_params)


        if not Confirm.ask("\nMake another request?", default=True): break

    save_history()
    console.print("👋 Goodbye!")
