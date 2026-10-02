import struct

from .format import (
    COB_MAGIC,
    COB_VERSION_MAJOR,
    COB_VERSION_MINOR,
    FLAG_DEBUG,
    HEADER_FORMAT,
    HEADER_SIZE,
    get_mode,
    mode_to_string,
)


def load_cob(path: str) -> dict:
    """
    Loads and validates a COB file.

    Returns a dictionary containing the data
    required by the CoreOS kernel/runtime.
    """

    # =====================================================
    # READ FILE
    # =====================================================

    with open(path, "rb") as file:
        data = file.read()

    # =====================================================
    # MINIMUM SIZE
    # =====================================================

    if len(data) < HEADER_SIZE:
        raise ValueError(
            "COB file is smaller than the fixed header"
        )

    # =====================================================
    # HEADER
    # =====================================================

    (
        magic,
        version_major,
        version_minor,
        flags,
        compatibility_layer,
        type_length,
        library_count,
        dynamic_library_count,
        header_size,
        code_size,
    ) = struct.unpack(
        HEADER_FORMAT,
        data[:HEADER_SIZE]
    )

    # =====================================================
    # MAGIC
    # =====================================================

    expected_magic = COB_MAGIC.to_bytes(
        3,
        byteorder="big"
    )

    if magic != expected_magic:
        raise ValueError(
            "Invalid COB magic"
        )

    # =====================================================
    # VERSION
    # =====================================================

    if version_major != COB_VERSION_MAJOR:
        raise ValueError(
            f"Unsupported COB major version: "
            f"{version_major}"
        )

    # =====================================================
    # HEADER SIZE
    # =====================================================

    if header_size < HEADER_SIZE:
        raise ValueError(
            "Invalid COB header size"
        )

    if header_size > len(data):
        raise ValueError(
            "COB header extends beyond file"
        )

    # =====================================================
    # VARIABLE DATA OFFSET
    # =====================================================

    offset = HEADER_SIZE

    # =====================================================
    # TYPE
    # =====================================================

    type_end = offset + type_length

    if type_end > header_size:
        raise ValueError(
            "Invalid COB type length"
        )

    cob_type = data[offset:type_end].decode(
        "utf-8"
    )

    offset = type_end

    # =====================================================
    # STATIC LIBRARIES
    # =====================================================

    libraries = []

    for _ in range(library_count):

        if offset + 2 > header_size:
            raise ValueError(
                "Invalid COB library entry"
            )

        library_length = struct.unpack(
            ">H",
            data[offset:offset + 2]
        )[0]

        offset += 2

        library_end = offset + library_length

        if library_end > header_size:
            raise ValueError(
                "Invalid COB library length"
            )

        library = data[
            offset:library_end
        ].decode("utf-8")

        libraries.append(library)

        offset = library_end

    # =====================================================
    # DYNAMIC LIBRARIES
    # =====================================================

    dynamic_libraries = []

    for _ in range(dynamic_library_count):

        if offset + 2 > header_size:
            raise ValueError(
                "Invalid COB dynamic library entry"
            )

        library_length = struct.unpack(
            ">H",
            data[offset:offset + 2]
        )[0]

        offset += 2

        library_end = offset + library_length

        if library_end > header_size:
            raise ValueError(
                "Invalid COB dynamic library length"
            )

        library = data[
            offset:library_end
        ].decode("utf-8")

        dynamic_libraries.append(library)

        offset = library_end

    # =====================================================
    # HEADER END
    # =====================================================

    if offset != header_size:
        raise ValueError(
            "COB header size does not match its contents"
        )

    # =====================================================
    # CODE
    # =====================================================

    code_start = header_size
    code_end = code_start + code_size

    if code_end > len(data):
        raise ValueError(
            "COB code extends beyond file"
        )

    code = data[
        code_start:code_end
    ].decode("utf-8")

    # =====================================================
    # FLAGS
    # =====================================================

    mode = get_mode(flags)

    return {
        "version": (
            version_major,
            version_minor,
        ),

        "type": cob_type,

        "mode": mode_to_string(mode),

        "debug": bool(
            flags & FLAG_DEBUG
        ),

        "compatibility_layer":
            compatibility_layer,

        "requirements": {
            "libraries": libraries,
            "dynamic_libraries":
                dynamic_libraries,
        },

        "code": code,
    }