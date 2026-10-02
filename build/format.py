import struct


# =========================================================
# COB
# =========================================================

COB_MAGIC = 0x020E01

COB_VERSION_MAJOR = 0
COB_VERSION_MINOR = 0


# Runtime modes
MODE_NORMAL = 0
MODE_STFN = 1
MODE_SDK = 2


# Flags
FLAG_DEBUG = 1 << 0

MODE_SHIFT = 1
MODE_MASK = 0b11 << MODE_SHIFT


# Compatibility layers
COMPATIBILITY_NONE = 0


# Fixed COB header
#
# 3 bytes  -> Magic
# 1 byte   -> Version Major
# 1 byte   -> Version Minor
# 4 bytes  -> Flags
# 1 byte   -> Compatibility Layer
# 2 bytes  -> Type Length
# 2 bytes  -> Library Count
# 2 bytes  -> Dynamic Library Count
# 4 bytes  -> Header Size
# 8 bytes  -> Code Size
#
HEADER_FORMAT = ">3sBBIBHHHIQ"

HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def mode_to_string(mode: int) -> str:
    if mode == MODE_NORMAL:
        return "normal"
    elif mode == MODE_STFN:
        return "stfn"
    elif mode == MODE_SDK:
        return "sdk"
    else:
        raise ValueError(f"Unknown COB mode: {mode}")


def get_mode(flags: int) -> int:
    return (flags & MODE_MASK) >> MODE_SHIFT


def set_mode(flags: int, mode: int) -> int:
    if mode not in (MODE_NORMAL, MODE_STFN, MODE_SDK):
        raise ValueError(f"Invalid COB mode: {mode}")

    flags &= ~MODE_MASK
    flags |= mode << MODE_SHIFT

    return flags