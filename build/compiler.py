import re
import struct

from format import (
    COB_MAGIC,
    COB_VERSION_MAJOR,
    COB_VERSION_MINOR,
    COMPATIBILITY_NONE,
    FLAG_DEBUG,
    HEADER_FORMAT,
    HEADER_SIZE,
    MODE_NORMAL,
    set_mode,
)


# =========================================================
# SOURCE ANALYSIS
# =========================================================

def check_libraries(code: str) -> list[str]:
    """
    Finds static libraries used by the COS source.
    """

    return re.findall(
        r'\brequire\s*\(\s*["\']([^"\']+)["\']\s*\)',
        code
    )


def check_dynamic_libraries(code: str) -> list[str]:
    """
    Finds dynamic libraries used by the COS source.
    """

    return re.findall(
        r'\brequire_dll\s*\(\s*["\']([^"\']+)["\']\s*\)',
        code
    )


# =========================================================
# COB COMPILER
# =========================================================

def build_cob(
    code: str,
    mode: int = MODE_NORMAL,
    debug: bool = False,
) -> bytes:
    """
    Converts COS source code into a COB file.

    Currently the source code itself is not transformed yet.
    It is stored as UTF-8 code inside the COB container.
    """
    basic = ""

    with open("src/basic.cos","r") as file:
        basic = file.read()

    libraries = check_libraries(code)
    dynamic_libraries = check_dynamic_libraries(code)

    # -----------------------------------------------------
    # NORMAL MODE
    # -----------------------------------------------------

    # Normal mode is CoreOS-only.
    # No external libraries are allowed.
    if mode == MODE_NORMAL:

        if libraries:
            raise ValueError(
                "Normal mode cannot use libraries: "
                + ", ".join(libraries)
            )

        if dynamic_libraries:
            raise ValueError(
                "Normal mode cannot use dynamic libraries: "
                + ", ".join(dynamic_libraries)
            )

    # -----------------------------------------------------
    # FLAGS
    # -----------------------------------------------------

    flags = 0

    flags = set_mode(flags, mode)

    if debug:
        flags |= FLAG_DEBUG

    # -----------------------------------------------------
    # MAGIC
    # -----------------------------------------------------

    magic = COB_MAGIC.to_bytes(
        3,
        byteorder="big"
    )

    # -----------------------------------------------------
    # TYPE
    # -----------------------------------------------------

    cob_type = "CoreOS Program"
    type_data = cob_type.encode("utf-8")

    # -----------------------------------------------------
    # CODE
    # -----------------------------------------------------

    code_data = (basic+ "\n" + code).encode("utf-8")

    # -----------------------------------------------------
    # HEADER SIZE
    # -----------------------------------------------------

    header_size = HEADER_SIZE + len(type_data)

    for library in libraries:

        library_data = library.encode("utf-8")

        header_size += 2
        header_size += len(library_data)

    for library in dynamic_libraries:

        library_data = library.encode("utf-8")

        header_size += 2
        header_size += len(library_data)

    # -----------------------------------------------------
    # FIXED HEADER
    # -----------------------------------------------------

    header = struct.pack(
        HEADER_FORMAT,
        magic,
        COB_VERSION_MAJOR,
        COB_VERSION_MINOR,
        flags,
        COMPATIBILITY_NONE,
        len(type_data),
        len(libraries),
        len(dynamic_libraries),
        header_size,
        len(code_data),
    )

    # -----------------------------------------------------
    # VARIABLE HEADER
    # -----------------------------------------------------

    variable_header = bytearray()

    # Type
    variable_header += type_data

    # Static libraries
    for library in libraries:

        library_data = library.encode("utf-8")

        variable_header += struct.pack(
            ">H",
            len(library_data)
        )

        variable_header += library_data

    # Dynamic libraries
    for library in dynamic_libraries:

        library_data = library.encode("utf-8")

        variable_header += struct.pack(
            ">H",
            len(library_data)
        )

        variable_header += library_data

    # -----------------------------------------------------
    # FINAL COB
    # -----------------------------------------------------

    return (
        header
        + variable_header
        + code_data
    )


def compile_file(
    input_path: str,
    output_path: str,
    mode: int = MODE_NORMAL,
    debug: bool = False,
) -> None:
    """
    Compiles a .cos file into a .cob file.
    """

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as file:

        code = file.read()

    cob_data = build_cob(
        code,
        mode=mode,
        debug=debug
    )

    with open(
        output_path,
        "wb"
    ) as file:

        file.write(cob_data)