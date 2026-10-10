"""Baked-in LabVIEW and NI error data, compiled from public sources.

Messages are quoted verbatim from National Instruments public documentation: the
LabVIEW Wiki "LabVIEW Error Code Family" page (general and network codes) and the NI
"LabVIEW Error Codes" manual (VISA codes). No message is invented: a code absent from
those sources carries no message and is classified only by the range it falls in.
"""

from __future__ import annotations

# code -> human description, verbatim from the sources above.
MESSAGES: dict[int, str] = {
    -1073807360: "Unknown system error (miscellaneous error).",
    -1073807346: "The given session or object reference is invalid.",
    -1073807344: "Invalid expression specified for search.",
    -1073807343: (
        "Insufficient location information, or the device or resource is not present in the system."
    ),
    -1073807342: "Invalid resource reference specified. Parsing error.",
    -1073807341: "Invalid access mode.",
    -1073807339: "Timeout expired before operation completed.",
    -1073807300: "Insufficient system resources to perform necessary memory allocation.",
    -1073807298: "Could not perform read/write operation because of I/O error.",
    -1073807297: "A format specifier in the format string is invalid.",
    -1073807231: "The given operation is not implemented.",
    1: (
        "An input parameter is invalid. For example if the input is a path, the path might "
        "contain a character not allowed by the OS such as ? or @."
    ),
    2: "Memory is full.",
    4: "End of file encountered.",
    5: "File already open.",
    6: "Generic file I/O error.",
    7: (
        "File not found. The file might be in a different location or deleted. Use the command "
        "prompt or the file explorer to verify that the path is correct."
    ),
    8: "File permission error. You do not have the correct permissions for the file.",
    9: (
        "Disk full. The disk or hard drive does not have enough free space to complete the "
        "operation. Try freeing up disk space or saving to a different disk or drive."
    ),
    10: "Duplicate path.",
    11: "Too many files open.",
    12: "Some system capacity necessary for operation is not enabled.",
    13: (
        "Failed to load dynamic library because of missing external symbols or dependencies, or "
        "because of an invalid file format."
    ),
    14: "Cannot add resource.",
    15: "Resource not found.",
    16: "Image not found.",
    24: "External subroutine not supported.",
    37: "Device not found.",
    42: "Generic error.",
    43: "Operation cancelled by user.",
    44: "Object ID too low.",
    53: "Manager call not supported.",
    54: (
        "The network address is ill-formed. Make sure the address is in a valid format. For "
        "TCP/IP, the address can be either a machine name or an IP address in the form "
        "xxx.xxx.xxx.xxx. If this error occurs when specifying a machine name, make sure the "
        "machine name is valid. Try to ping the machine name. Check that you have a DNS server "
        "properly configured. If you are using the TCP Open Connection function, ensure that the "
        "value of the remote port or service name is not 0."
    ),
    55: "The network operation is in progress.",
    56: "The network operation exceeded the user-specified or system time limit.",
    57: "The network connection is busy.",
    58: "The network function is not supported by the system.",
    59: "The network is down, unreachable, or has been reset.",
    60: (
        "The specified port or network address is currently in use. Select an available port or "
        "network address."
    ),
    66: (
        "The network connection was closed by the peer. If you are using the Open VI Reference "
        "function on a remote VI Server connection, verify that the machine is allowed access by "
        "selecting Tools>>Options>>VI Server on the server side."
    ),
    116: (
        "Unflatten or byte stream read operation failed due to corrupt, unexpected, or truncated "
        "data."
    ),
    1026: "VI Reference is invalid.",
    1027: (
        "For the requested operation, the reference cannot be reserved as requested, is in an "
        "improper reservation mode, or the execution state must be set to running or reserved."
    ),
    1055: "Object reference is invalid.",
    1097: (
        "An exception occurred within the external code called by a Call Library Function Node. "
        "The exception might have corrupted the LabVIEW memory. Save any work to a new location "
        "and restart LabVIEW."
    ),
    1100: "No object of that name was found. No reference could be returned.",
    1172: (
        "A .NET exception occurred in an external assembly. For information about correcting this "
        "error, copy the following exception (in bold), and search the Microsoft Developer "
        "Network (MSDN) Web site or the Web for a possible explanation."
    ),
    1357: (
        "A LabVIEW file from that path already exists in memory, or exists within a project "
        "library already in memory."
    ),
    1430: "The path is empty or relative. You must use an absolute path.",
    1556: (
        "The reference is invalid. This error might occur because the reference has been deleted."
    ),
    1671: "There was an error in executing the specified function.",
    1672: "There was an unknown Python error in the operation.",
    1761: (
        "The Python DLL of the specified version cannot be loaded at the specified path. Possible "
        "reasons include bitness mismatch between Python DLL and LabVIEW that opens the Python "
        "session, or a corrupt Python DLL file."
    ),
}

# Positive codes that denote errors, not warnings. LabVIEW's legacy general and
# network families number some errors with small positive values, against the usual
# "positive means warning" convention; every positive code shipped here is such an error.
POSITIVE_ERROR_CODES: frozenset[int] = frozenset(c for c in MESSAGES if c > 0)

# Documented numeric ranges, most specific first. Each tuple is (low, high, family).
# Sources: NI "Ranges of LabVIEW Error Codes" (families and the custom-code ranges) and
# the NI "LabVIEW Error Codes" manual. Some codes belong to more than one family (NI
# notes, for example, that 65 is both a serial and a network code); the first match wins,
# so the more specific family is the one reported.
RANGES: tuple[tuple[int, int, str], ...] = (
    (-209999, -200000, "NI-DAQmx"),
    (-20065, -20001, "analysis VI"),
    (-10943, -10001, "data acquisition VI"),
    (-8999, -8000, "user-defined"),
    (-1719, -1700, "AppleEvent"),
    (-1399, -1200, "instrument driver"),
    (-932, -900, "PPC"),
    (-1073807360, -1073807231, "VISA"),
    (53, 66, "network"),
    (5000, 9999, "user-defined"),
    (14001, 14020, "DDE"),
    (200000, 209999, "NI-DAQmx"),
    (500000, 599999, "user-defined"),
    (1, 16000, "general LabVIEW"),
)
