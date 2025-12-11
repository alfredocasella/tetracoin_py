import unittest
import pathlib
import re

LEGACY_IMPORTS = [
    "old_engine",
    "legacy_physics",
    "coin_drop_legacy",
    "v1_solver",
    "old_grid",
    "old_utils",
    "core.grid_manager", # Recently archived
]

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIRS = ["src", "tetracoin", "game", "core", "tools"]

class TestNoLegacyImports(unittest.TestCase):
    def test_no_legacy_imports(self):
        pattern = re.compile(
            r"^(from|import)\s+(" + "|".join(re.escape(x) for x in LEGACY_IMPORTS) + r")\b"
        )
        violations = []
        
        for src_dir_name in SRC_DIRS:
            base = PROJECT_ROOT / src_dir_name
            if not base.is_dir():
                continue
                
            for path in base.rglob("*.py"):
                # Skip archived directory if inside one of SRC_DIRS (though usually archived is root)
                if "archived" in str(path):
                    continue
                    
                text = path.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(text.splitlines(), start=1):
                    # Check uncommented lines only roughly
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                        
                    if pattern.search(stripped):
                        violations.append(f"{path}:{i}: {line.strip()}")
                        
        self.assertFalse(violations, "Legacy imports found:\n" + "\n".join(violations))

if __name__ == '__main__':
    unittest.main()
