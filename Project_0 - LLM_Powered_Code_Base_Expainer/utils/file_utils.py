import zipfile, os, glob
import nbformat

def extract_zip_and_get_code_files(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    code_files = glob.glob(os.path.join(extract_dir, "**", "*.*"), recursive=True)
    return [f for f in code_files if f.endswith((".py", ".ipynb"))]

def extract_code_from_notebook(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        code_cells = [cell['source'] for cell in nb.cells if cell.cell_type == 'code']
        return "\n\n".join(code_cells)
    except Exception as e:
        return f"# Could not parse notebook: {e}"

def build_file_tree(file_paths, root_dir):
    tree = {}
    for path in file_paths:
        rel_path = os.path.relpath(path, root_dir)
        parts = rel_path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = path
    return tree
