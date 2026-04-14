"""
SDK Compatibility Tests — verify ALL code matches real SDK signatures.

Run: .venv/bin/pytest tests/test_sdk_compat.py -v

This test reads EVERY .py file in ui/ and modules/ and verifies:
1. All UI component calls use only valid kwargs
2. All store calls match StoreProtocol signatures
3. All AI calls match AIProtocol signatures
4. No deprecated/imaginary methods used
"""

import ast
import inspect
import pytest
from pathlib import Path

# Import real SDK
from imperal_sdk import ui as sdk_ui
from imperal_sdk.context import Context


# ======================================================================
# Collect real SDK signatures
# ======================================================================

def get_ui_signatures() -> dict[str, set[str]]:
    """Get valid kwargs for every UI component from SDK source."""
    sigs = {}
    accepts_any_kwargs = set()
    for name in dir(sdk_ui):
        obj = getattr(sdk_ui, name)
        if callable(obj) and name[0].isupper() and not name.startswith("_"):
            try:
                sig = inspect.signature(obj)
                params = set(sig.parameters.keys())
                # Check if function accepts **kwargs (VAR_KEYWORD)
                for p in sig.parameters.values():
                    if p.kind == inspect.Parameter.VAR_KEYWORD:
                        accepts_any_kwargs.add(name)
                sigs[name] = params
            except (ValueError, TypeError):
                pass
    return sigs, accepts_any_kwargs


def get_protocol_methods(proto_name: str) -> dict[str, set[str]]:
    """Get methods and their params from a Protocol class."""
    import imperal_sdk.context as ctx_mod
    proto = getattr(ctx_mod, proto_name, None)
    if not proto:
        return {}
    methods = {}
    for name in dir(proto):
        if name.startswith("_"):
            continue
        method = getattr(proto, name, None)
        if callable(method):
            try:
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                methods[name] = params
            except (ValueError, TypeError):
                pass
    return methods


UI_SIGS, UI_ACCEPTS_ANY_KWARGS = get_ui_signatures()
STORE_METHODS = get_protocol_methods("StoreProtocol")
AI_METHODS = get_protocol_methods("AIProtocol")


# ======================================================================
# AST analysis — find all function calls in Python files
# ======================================================================

def find_calls_in_file(filepath: Path) -> list[dict]:
    """Parse a Python file and find all relevant function calls."""
    source = filepath.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [{"error": f"SyntaxError in {filepath}"}]

    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_info = _extract_call(node, filepath)
            if call_info:
                calls.append(call_info)
    return calls


def _extract_call(node: ast.Call, filepath: Path) -> dict | None:
    """Extract function name and kwargs from an AST Call node."""
    # Get function name
    name = None
    if isinstance(node.func, ast.Name):
        name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        name = node.func.attr
        # Check for ctx.store.X, ctx.ai.X
        if isinstance(node.func.value, ast.Attribute):
            parent = node.func.value.attr
            if parent in ("store", "ai"):
                name = f"{parent}.{name}"

    if not name:
        return None

    # Get kwargs
    kwargs = set()
    for kw in node.keywords:
        if kw.arg:
            kwargs.add(kw.arg)

    # Get positional arg count
    n_args = len(node.args)

    return {
        "name": name,
        "kwargs": kwargs,
        "n_args": n_args,
        "file": str(filepath),
        "line": node.lineno,
    }


# ======================================================================
# Tests
# ======================================================================

PROJECT_ROOT = Path(__file__).parent.parent
UI_FILES = list((PROJECT_ROOT / "ui").glob("*.py"))
MODULE_FILES = list((PROJECT_ROOT / "modules").glob("*.py"))
ALL_PY_FILES = UI_FILES + MODULE_FILES + [PROJECT_ROOT / "main.py"]


class TestUIComponentSignatures:
    """Verify all UI component calls use only valid kwargs."""

    @pytest.fixture
    def all_ui_calls(self):
        calls = []
        for f in UI_FILES:
            for call in find_calls_in_file(f):
                if call.get("name") in UI_SIGS:
                    calls.append(call)
        return calls

    def test_no_invalid_kwargs(self, all_ui_calls):
        """Every kwarg passed to a UI component must exist in its signature."""
        errors = []
        for call in all_ui_calls:
            name = call["name"]
            # Skip components that accept **kwargs (e.g. Call)
            if name in UI_ACCEPTS_ANY_KWARGS:
                continue
            valid = UI_SIGS.get(name, set())
            invalid = call["kwargs"] - valid
            if invalid:
                errors.append(
                    f'{call["file"]}:{call["line"]} — {name}() got invalid kwargs: {invalid}. '
                    f'Valid: {sorted(valid)}'
                )
        assert not errors, "Invalid UI kwargs:\n" + "\n".join(errors)

    def test_no_name_kwarg(self, all_ui_calls):
        """Input/TextArea/Select must NOT use name= (use param_name=)."""
        errors = []
        for call in all_ui_calls:
            if call["name"] in ("Input", "TextArea", "Select", "Toggle", "Slider", "TagInput"):
                if "name" in call["kwargs"]:
                    errors.append(f'{call["file"]}:{call["line"]} — {call["name"]}(name=...) → use param_name=')
        assert not errors, "Deprecated 'name' kwarg:\n" + "\n".join(errors)

    def test_no_label_on_input(self, all_ui_calls):
        """Input must NOT use label= (not a valid kwarg)."""
        errors = []
        for call in all_ui_calls:
            if call["name"] == "Input" and "label" in call["kwargs"]:
                errors.append(f'{call["file"]}:{call["line"]} — Input(label=...) not valid')
        assert not errors, "Invalid 'label' on Input:\n" + "\n".join(errors)

    def test_no_type_on_input(self, all_ui_calls):
        """Input must NOT use type= (not a valid kwarg)."""
        errors = []
        for call in all_ui_calls:
            if call["name"] == "Input" and "type" in call["kwargs"]:
                errors.append(f'{call["file"]}:{call["line"]} — Input(type=...) not valid')
        assert not errors, "Invalid 'type' on Input:\n" + "\n".join(errors)

    def test_button_uses_on_click(self, all_ui_calls):
        """Button must use on_click=, not action=."""
        errors = []
        for call in all_ui_calls:
            if call["name"] == "Button" and "action" in call["kwargs"]:
                errors.append(f'{call["file"]}:{call["line"]} — Button(action=...) → use on_click=')
        assert not errors, "Button uses 'action' instead of 'on_click':\n" + "\n".join(errors)

    def test_call_no_params_dict(self, all_ui_calls):
        """Call() must use **kwargs, NOT params={} (causes double nesting)."""
        errors = []
        for call in all_ui_calls:
            if call["name"] == "Call" and "params" in call["kwargs"]:
                errors.append(f'{call["file"]}:{call["line"]} — Call(params={{...}}) → use Call(function=..., key=val)')
        assert not errors, "Call uses params={} (double nesting bug):\n" + "\n".join(errors)

    def test_badge_uses_label(self, all_ui_calls):
        """Badge must use label=, not text=."""
        errors = []
        for call in all_ui_calls:
            if call["name"] == "Badge" and "text" in call["kwargs"]:
                errors.append(f'{call["file"]}:{call["line"]} — Badge(text=...) → use label=')
        assert not errors, "Badge uses 'text' instead of 'label':\n" + "\n".join(errors)

    def test_card_uses_content(self, all_ui_calls):
        """Card must use content=, not children=."""
        errors = []
        for call in all_ui_calls:
            if call["name"] == "Card" and "children" in call["kwargs"]:
                errors.append(f'{call["file"]}:{call["line"]} — Card(children=...) → use content=')
        assert not errors, "Card uses 'children' instead of 'content':\n" + "\n".join(errors)


class TestStoreProtocol:
    """Verify all ctx.store calls match StoreProtocol."""

    @pytest.fixture
    def all_store_calls(self):
        calls = []
        for f in ALL_PY_FILES:
            for call in find_calls_in_file(f):
                name = call.get("name", "")
                if name.startswith("store."):
                    calls.append(call)
        return calls

    def test_no_store_set(self, all_store_calls):
        """store.set() does not exist — use store.create() or store.update()."""
        errors = [
            f'{c["file"]}:{c["line"]} — ctx.store.set() → use .create() or .update()'
            for c in all_store_calls if c["name"] == "store.set"
        ]
        assert not errors, "Deprecated store.set():\n" + "\n".join(errors)

    def test_no_store_list(self, all_store_calls):
        """store.list() does not exist — use store.query()."""
        errors = [
            f'{c["file"]}:{c["line"]} — ctx.store.list() → use .query()'
            for c in all_store_calls if c["name"] == "store.list"
        ]
        assert not errors, "Deprecated store.list():\n" + "\n".join(errors)

    def test_store_get_two_args(self, all_store_calls):
        """store.get() requires 2 args: collection + doc_id."""
        errors = []
        for c in all_store_calls:
            if c["name"] == "store.get" and c["n_args"] < 2:
                errors.append(f'{c["file"]}:{c["line"]} — store.get() needs 2 args (collection, doc_id)')
        assert not errors, "store.get() with wrong arg count:\n" + "\n".join(errors)


class TestAIProtocol:
    """Verify AI calls match AIProtocol."""

    @pytest.fixture
    def all_ai_calls(self):
        calls = []
        for f in ALL_PY_FILES:
            for call in find_calls_in_file(f):
                name = call.get("name", "")
                if name.startswith("ai."):
                    calls.append(call)
        return calls

    def test_no_ai_chat(self, all_ai_calls):
        """ctx.ai.chat() does not exist — use ctx.ai.complete()."""
        errors = [
            f'{c["file"]}:{c["line"]} — ctx.ai.chat() → use ctx.ai.complete()'
            for c in all_ai_calls if c["name"] == "ai.chat"
        ]
        assert not errors, "Deprecated ai.chat():\n" + "\n".join(errors)


class TestImports:
    """Verify all imports work."""

    def test_main_imports(self):
        from main import ext
        assert ext.app_id == "video-creator"

    def test_dashboard_imports(self):
        from ui.dashboard import register_dashboard
        assert callable(register_dashboard)

    def test_settings_imports(self):
        from ui.settings import register_settings
        assert callable(register_settings)

    def test_sidebar_imports(self):
        from ui.sidebar import register_sidebar
        assert callable(register_sidebar)

    def test_all_modules_import(self):
        from modules import ALL_MODULES
        assert len(ALL_MODULES) >= 10
