import argparse

from compiler import compile_file

from format import (
    MODE_NORMAL,
    MODE_STFN,
    MODE_SDK,
)

def parse_args():

    parser = argparse.ArgumentParser(
        description="CoreOS COS Compiler"
    )

    # -----------------------------------------------------
    # INPUT
    # -----------------------------------------------------

    parser.add_argument(
        "input",
        help="Input COS source file"
    )

    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output COB file"
    )

    # -----------------------------------------------------
    # MODE
    # -----------------------------------------------------

    mode_group = parser.add_mutually_exclusive_group()

    mode_group.add_argument(
        "--normal",
        action="store_true",
        help="Build for normal CoreOS runtime"
    )

    mode_group.add_argument(
        "--stfn",
        action="store_true",
        help="Build for STFN runtime"
    )

    mode_group.add_argument(
        "--sdk",
        action="store_true",
        help="Build for COS SDK runtime"
    )

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include debug information"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    output = args.output

    if output is None:

        if args.input.endswith(".cos"):
            output = (
                args.input[:-4]
                + ".cob"
            )

        else:
            output = args.input + ".cob"

    # -----------------------------------------------------
    # MODE
    # -----------------------------------------------------

    if args.sdk:

        mode = MODE_SDK

    elif args.stfn:

        mode = MODE_STFN

    else:

        mode = MODE_NORMAL

    # -----------------------------------------------------
    # BUILD
    # -----------------------------------------------------

    try:

        compile_file(
            args.input,
            output,
            mode=mode,
            debug=args.debug
        )

    except Exception as error:

        print(
            f"Build failed: {error}"
        )

        return 1

    print(
        f"Built: {args.input} -> {output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())