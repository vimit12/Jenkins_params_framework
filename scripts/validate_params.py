# scripts/validate_params.py
import argparse
import sys
from jenkins_param_validator.engine import validate_params, ValidationError


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
        print("\n❌ Parameter validation failed\n")
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print("\n💥 Unexpected error during validation\n")
        print(repr(e))
        sys.exit(2)

    print("\n✅ Parameters validated successfully\n")


if __name__ == "__main__":
    main()