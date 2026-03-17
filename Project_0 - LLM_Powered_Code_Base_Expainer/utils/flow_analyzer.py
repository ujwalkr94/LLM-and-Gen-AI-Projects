import ast
import os

class FileFlowAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.called_functions = []
        self.imports = []
        self.main_block = False

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module if node.module else ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)

    def visit_If(self, node):
        # Check for: if __name__ == "__main__":
        if isinstance(node.test, ast.Compare):
            left = getattr(node.test.left, 'id', None)
            if left == "__name__":
                self.main_block = True
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called_functions.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called_functions.append(node.func.attr)
        self.generic_visit(node)

def analyze_code_flow(base_path):
    summary = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_path)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    analyzer = FileFlowAnalyzer(file_path)
                    analyzer.visit(tree)

                    flow = {
                        "file": rel_path,
                        "imports": analyzer.imports,
                        "calls": analyzer.called_functions,
                        "has_main": analyzer.main_block
                    }
                    summary.append(flow)
                except Exception as e:
                    print(f"⚠️ Failed to parse {rel_path}: {e}")

    return summary
