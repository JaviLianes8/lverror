"""General LabVIEW error codes up to 131, and the COM/HRESULT codes LabVIEW surfaces.

Messages are compiled from public National Instruments documentation (the NI "General
LabVIEW Error Codes" reference) and the community LabVIEW Wiki error-code pages. No message
is invented. Codes 61 to 65 are documented with two meanings, a serial-port meaning and a
network meaning, and both are given.
"""

from __future__ import annotations

GENERAL_LOW: dict[int, str] = {
    -2147483638: "Data needed for the operation is not yet available.",
    -2147467263: "The requested feature is not implemented.",
    -2147467262: "No such interface is supported.",
    -2147467261: "An invalid pointer was used.",
    -2147467260: "The operation was aborted.",
    -2147467259: "An unspecified error occurred.",
    -2147418113: "A catastrophic failure occurred.",
    -2147024891: "Access is denied.",
    -2147024890: "An invalid handle was used.",
    -2147024882: "The system ran out of memory.",
    -2147024809: "One or more arguments are invalid.",
    1: (
        "An input parameter is invalid. For example if the input is a path, the path might contain "
        "a character not allowed by the OS such as ? or @."
    ),
    2: "Memory is full.",
    3: "Internal error: an incorrect memory zone was accessed.",
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
    11: "Too many files are open.",
    12: "Some system capacity necessary for the operation is not enabled.",
    13: (
        "Failed to load dynamic library because of missing external symbols or dependencies, or "
        "because of an invalid file format."
    ),
    14: "Cannot add a resource.",
    15: "Resource not found.",
    16: "Image not found.",
    17: "Not enough memory to manipulate the image.",
    18: "The pen does not exist.",
    19: "The configuration data type is invalid.",
    20: "The configuration token was not found.",
    21: "Error parsing a configuration string.",
    22: "Configuration memory error.",
    23: "Bad external code format.",
    24: "External subroutine not supported.",
    25: "External code is not present.",
    26: "Null window.",
    27: "Error destroying a window.",
    28: "Null menu.",
    29: "Printing was aborted.",
    30: "Bad print record.",
    31: "Print driver error.",
    32: "Operating system error during printing.",
    33: "Memory error during printing.",
    34: "Print dialog error.",
    35: "Generic print error.",
    36: "Invalid device refnum.",
    37: "Device not found.",
    38: "Device parameter error.",
    39: "Device unit error.",
    40: "Cannot open the device.",
    41: "The device call was aborted.",
    42: "Generic error.",
    43: "Operation cancelled by user.",
    44: "Object ID too low.",
    45: "Object ID too high.",
    46: "Object is not in the heap.",
    47: "Unknown heap.",
    48: "Unknown object, the DefProc is invalid.",
    49: "Unknown object, the DefProc is not in the table.",
    50: "The message is out of range.",
    51: "Null method.",
    52: "Unknown message.",
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
    61: "Serial port parity error. Also: could not allocate the necessary memory.",
    62: "Serial port overrun error. Also: the system aborted the network connection.",
    63: (
        "Serial port receive buffer overflow. Also: the network connection was refused by the "
        "server."
    ),
    64: "Serial port framing error. Also: the network connection has not yet been established.",
    65: (
        "Serial port timeout, bytes not received. Also: the network connection is already "
        "established."
    ),
    66: (
        "The network connection was closed by the peer. If you are using the Open VI Reference "
        "function on a remote VI Server connection, verify that the machine is allowed access by "
        "selecting Tools>>Options>>VI Server on the server side."
    ),
    67: "Interapplication Manager initialization error.",
    68: "Bad occurrence.",
    69: "The handler does not know which occurrence to wait for.",
    70: "The occurrence queue overflowed.",
    71: "File datalog type conflict.",
    72: "Semaphore not signaled.",
    73: "Interapplication Manager unrecognized type error.",
    74: "Memory or data structure is corrupt.",
    75: "Failed to make a temporary DLL.",
    76: "Old CIN version.",
    81: "Format specifier type mismatch.",
    82: "Unknown format specifier.",
    83: "Too few format specifiers.",
    84: "Too many format specifiers.",
    85: "Scan failed, the input string was not in the expected format.",
    87: "Error converting to a variant.",
    88: "Run-time menu error.",
    89: "Another user tampered with the VI password.",
    90: "Variant attribute not found.",
    91: "The variant data type is incompatible with the type input.",
    92: "ActiveX event data is not available on the queue.",
    93: "ActiveX event information is not available.",
    94: "ActiveX event occurrence not found.",
    95: "The ActiveX event queue could not be created.",
    96: "ActiveX event information is not in the type library.",
    97: "A null or previously deleted refnum was passed as an input.",
    98: "Incorrect file type.",
    99: "Incorrect file version.",
    100: "The file contains erroneous data.",
    102: "IVI invalid downcast.",
    103: "No IVI class session was opened.",
    108: "Singlecast connections cannot send to multicast addresses.",
    109: "Multicast connections cannot send to singlecast addresses.",
    110: "The IP address is not in the multicast range.",
    111: "Cannot write to a read-only multicast connection.",
    112: "Cannot read from a write-only multicast connection.",
    113: "The datagram is larger than the buffer or the network limit.",
    114: "The TCP listener port conflicts with an existing listener.",
    116: (
        "Unflatten or byte stream read operation failed due to corrupt, unexpected, or truncated "
        "data."
    ),
    117: "A directory path was supplied where a file path is required.",
    118: "The supplied folder path does not exist.",
    119: "Illegal combination of Bluetooth discoverable and non-connectable modes.",
    120: "Error setting the Bluetooth mode.",
    121: "Invalid GUID string.",
    122: "The resource was created in a more recent version of LabVIEW.",
    123: "A timeout occurred.",
    124: "The string contained an unexpected null character.",
    125: "A stack overflow occurred.",
    126: "Could not query the socket state.",
    127: "The specified socket is not IPv4.",
    128: "The open connection limit was exceeded.",
    129: "The access path is too long for the operating system.",
    130: "Set creation was attempted with duplicate elements.",
    131: "Map creation was attempted with duplicate keys.",
}
