import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import yaml

from app.main import app


def export_openapi() -> None:
    schema = app.openapi()
    output_path = root_dir / "openapi.yaml"

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(schema, f, sort_keys=False, allow_unicode=True)

    print(f"Спецификация OpenAPI успешно сохранена в: {output_path}")


if __name__ == "__main__":
    export_openapi()
