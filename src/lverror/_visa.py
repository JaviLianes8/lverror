"""NI-VISA completion, warning and error codes.

Compiled from public National Instruments documentation (the NI-VISA C API reference and
the LabVIEW VISA error-code page). The positive completion and warning codes are listed in
``VISA_WARNING_CODES`` so they are not misreported as errors. No message is invented.
"""

from __future__ import annotations

VISA: dict[int, str] = {
    1073676290: (
        "The specified event is already enabled for at least one of the specified mechanisms."
    ),
    1073676291: (
        "The specified event is already disabled for at least one of the specified mechanisms."
    ),
    1073676292: "The operation completed successfully, but the queue was already empty.",
    1073676293: "The specified termination character was read.",
    1073676294: "The number of bytes read is equal to the input count.",
    1073676300: (
        "The event returned is valid. One or more events that occurred have not been raised "
        "because there was no room on the queue at the time of their occurrence."
    ),
    1073676407: (
        "The specified configuration does not exist or could not be loaded, VISA-specified "
        "defaults are used."
    ),
    1073676413: (
        "The session opened successfully, but the device at the specified address is not "
        "responding."
    ),
    1073676414: "The path from trigSrc to trigDest is already mapped.",
    1073676416: (
        "The wait terminated successfully on receipt of an event notification. There is still at "
        "least one more event occurrence of the requested type available for this session."
    ),
    1073676418: "The specified object reference is uninitialized.",
    1073676420: (
        "The specified state of the attribute is valid, but it is not supported by this resource."
    ),
    1073676421: "The status code passed to the operation could not be interpreted.",
    1073676424: "The specified buffer is not supported.",
    1073676440: (
        "The event was handled successfully. Do not invoke any other handlers on this session for "
        "this event."
    ),
    1073676441: "The operation completed successfully, and this session has nested shared locks.",
    1073676442: (
        "The operation completed successfully, and this session has nested exclusive locks."
    ),
    1073676443: "The asynchronous operation request was actually performed synchronously.",
    1073676457: (
        "The operation succeeded, but a lower level driver did not implement the extended "
        "functionality."
    ),
    -1073807360: "Unknown system error (miscellaneous error).",
    -1073807346: "The given session or object reference is invalid.",
    -1073807345: (
        "The specified lock cannot be obtained or the operation cannot be performed because the "
        "resource is locked."
    ),
    -1073807344: "Invalid expression specified for search.",
    -1073807343: (
        "Insufficient location information, or the device or resource is not present in the system."
    ),
    -1073807342: "Invalid resource reference specified. Parsing error.",
    -1073807341: "Invalid access mode.",
    -1073807339: "Timeout expired before operation completed.",
    -1073807338: (
        "Unable to deallocate the data structures corresponding to this session or object "
        "reference."
    ),
    -1073807333: "The specified degree is invalid.",
    -1073807332: "The specified job identifier is invalid.",
    -1073807331: (
        "The specified attribute is not defined or supported by the referenced session, event, or "
        "find list."
    ),
    -1073807330: (
        "The specified state of the attribute is not valid, or is not supported by the session, "
        "event, or find list."
    ),
    -1073807329: "The specified attribute is read-only.",
    -1073807328: "The specified type of lock is not supported by this resource.",
    -1073807327: "The access key to the resource associated with this session is invalid.",
    -1073807322: "The specified event type is not supported by the resource.",
    -1073807321: "Invalid mechanism specified.",
    -1073807320: "A handler is not currently installed for the specified event.",
    -1073807319: "The given handler reference is invalid.",
    -1073807318: "The specified event context is invalid.",
    -1073807315: (
        "The event queue for the specified type has overflowed, usually because previous events "
        "were not closed."
    ),
    -1073807313: (
        "The session must be enabled for events of the specified type in order to receive them."
    ),
    -1073807312: "The operation was aborted.",
    -1073807308: "Violation of raw write protocol occurred during transfer.",
    -1073807307: "Violation of raw read protocol occurred during transfer.",
    -1073807306: "The device reported an output protocol error during transfer.",
    -1073807305: "The device reported an input protocol error during transfer.",
    -1073807304: "A bus error occurred during transfer.",
    -1073807303: (
        "Unable to queue the asynchronous operation because an operation is already in progress."
    ),
    -1073807302: (
        "Unable to start the operation because the setup is invalid, due to attributes set to an "
        "inconsistent state."
    ),
    -1073807301: (
        "Unable to queue the asynchronous operation, usually because the completion event is not "
        "enabled or the queue is full."
    ),
    -1073807300: "Insufficient system resources to perform necessary memory allocation.",
    -1073807299: "Invalid buffer mask specified.",
    -1073807298: "Could not perform read/write operation because of I/O error.",
    -1073807297: "A format specifier in the format string is invalid.",
    -1073807295: "A format specifier in the format string is not supported.",
    -1073807294: "The specified trigger line is currently in use.",
    -1073807290: "The specified mode is not supported by this VISA implementation.",
    -1073807286: "A service request has not been received for the session.",
    -1073807282: "Invalid address space specified.",
    -1073807279: "Invalid offset specified.",
    -1073807278: "Invalid source or destination width specified.",
    -1073807276: "The specified offset is not accessible from this hardware.",
    -1073807275: "Cannot support source and destination widths that are different.",
    -1073807273: "The specified session is not currently mapped.",
    -1073807271: "A previous response is still pending, causing a multiple query error.",
    -1073807265: "A No Listeners condition was detected (both NRFD and NDAC are deasserted).",
    -1073807264: (
        "The interface associated with this session is not currently the controller in charge."
    ),
    -1073807263: "The interface associated with this session is not the system controller.",
    -1073807257: "The given session or object reference does not support this operation.",
    -1073807256: "An interrupt is still pending from a previous call.",
    -1073807254: "A parity error occurred during transfer.",
    -1073807253: "A framing error occurred during transfer.",
    -1073807252: (
        "An overrun error occurred during transfer. A character was not read before the next one "
        "arrived."
    ),
    -1073807250: "The path from trigSrc to trigDest is not currently mapped.",
    -1073807248: (
        "The specified offset is not properly aligned for the access width of the operation."
    ),
    -1073807247: (
        "A specified user buffer is not valid or cannot be accessed for the required size."
    ),
    -1073807246: "The resource is valid, but VISA cannot currently access it.",
    -1073807242: "The specified width is not supported by this hardware.",
    -1073807240: "The value of some parameter (which parameter is not known) is invalid.",
    -1073807239: "The protocol specified is invalid.",
    -1073807237: "Invalid size of window specified.",
    -1073807232: "The specified session currently contains a mapped window.",
    -1073807231: "The given operation is not implemented.",
    -1073807229: "Invalid length specified.",
    -1073807215: "The specified mode is invalid.",
    -1073807204: "The current session did not have any lock on the resource.",
    -1073807203: "The device does not export any memory.",
    -1073807202: "A code library required by VISA could not be located or loaded.",
    -1073807201: (
        "The interface cannot generate an interrupt on the requested level or with the requested "
        "statusID."
    ),
    -1073807200: "The value specified by the line parameter is invalid.",
    -1073807199: (
        "An error occurred while trying to open the specified file, such as an invalid path or "
        "lack of access rights."
    ),
    -1073807198: "An error occurred while performing I/O on the specified file.",
    -1073807197: (
        "One of the specified trigger lines is not supported, or the combination of lines is not a "
        "valid mapping."
    ),
    -1073807196: "The specified mechanism is not supported for the given event type.",
    -1073807195: (
        "The interface type is valid but the specified interface number is not configured."
    ),
    -1073807194: "The connection for the given session has been lost.",
    -1073807193: "The remote machine does not exist or is not accepting any connections.",
    -1073807192: (
        "Access to the resource or remote machine is denied due to insufficient privileges."
    ),
}

# Positive VISA completion and warning codes: not errors despite being documented.
VISA_WARNING_CODES: frozenset[int] = frozenset(c for c in VISA if c > 0)
