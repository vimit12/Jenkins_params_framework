# scripts/validate_params.py
import argparse
import sys
import os
import json

# Add workspace root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jenkins_param_validator.engine import validate_params, ValidationError
from rich.console import Console
from rich.table import Table

console = Console()


def display_error_table(errors):
    """Display validation errors in a formatted table"""
    table = Table(title="❌ Validation Error Details", show_header=True, header_style="bold red")
    table.add_column("Field Name", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_column("Type", style="magenta")
    table.add_column("Error", style="red")

    for error in errors:
        table.add_row(
            error.get("field", "unknown"),
            str(error.get("value", "N/A"))[:50],  # Truncate long values
            error.get("type", "unknown"),
            error.get("error", "Unknown error")
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input.json")
    parser.add_argument("--schema", required=True, help="Path to schema.json")
    parser.add_argument("--no-coerce", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    try:
        validate_params(
            input_file=args.input,
            schema_file=args.schema,
            coerce=not args.no_coerce,
            strict=args.strict,
        )
    except ValidationError as e:
        console.print("\n[bold red]Parameter Validation Failed[/bold red]\n")
        if e.errors:
            display_error_table(e.errors)
        else:
            console.print(f"[red]{str(e)}[/red]")
        console.print()
        sys.exit(1)
    except Exception as e:
        console.print("\n[bold red]💥 Unexpected Error During Validation[/bold red]\n")
        console.print(f"[red]{repr(e)}[/red]\n")
        sys.exit(2)

    console.print("\n[bold green]✅ Parameters Validated Successfully![/bold green]\n")


if __name__ == "__main__":
    main()