"""Other documented LabVIEW error families: instrument driver, AppleEvent, PPC, DDE and networking.

Compiled from public National Instruments documentation (the NI "LabVIEW Error Codes"
reference) and the community LabVIEW Wiki error-code pages. No message is invented. Small
positive codes that these families reuse (GPIB, serial and PPC-specific codes) are omitted
here because the same integers carry the general LabVIEW meaning, which is the default.
"""

from __future__ import annotations

FAMILIES: dict[int, str] = {
    -1200: "Invalid syntax string.",
    -1201: "Error finding instruments.",
    -1202: "Unable to initialize the interface or instrument.",
    -1205: "Invalid instrument handle.",
    -1210: "Parameter out of range.",
    -1215: "Error closing the instrument.",
    -1218: "Error getting an attribute.",
    -1219: "Error setting an attribute.",
    -1223: "The instrument identification query failed.",
    -1224: "Error clearing the instrument.",
    -1225: "Error triggering the instrument.",
    -1226: "Error polling the instrument.",
    -1230: "Error writing to the instrument.",
    -1231: "Error reading from the instrument.",
    -1236: "Error interpreting the instrument response.",
    -1240: "The instrument timed out.",
    -1250: "Error mapping a VXI address.",
    -1251: "Error unmapping a VXI address.",
    -1252: "Error accessing a VXI address.",
    -1260: "The function is not supported by the controller.",
    -1300: "Instrument-specific error.",
    -1700: "The data could not be coerced to the requested descriptor type.",
    -1701: "The descriptor record was not found.",
    -1702: "The data in an Apple event could not be read.",
    -1703: "Wrong descriptor type.",
    -1704: "Not a valid descriptor record.",
    -1705: "An operation involving a list item failed.",
    -1706: "A newer version of the AppleEvent Manager is needed.",
    -1707: "The event is not an Apple event.",
    -1708: "AEResetTimer was passed an invalid reply parameter.",
    -1709: "AEResetTimer was passed an invalid reply parameter.",
    -1710: "An invalid sending mode was passed.",
    -1711: "The user canceled out of the wait loop for a reply or receipt.",
    -1712: "The Apple event timed out.",
    -1713: "No user interaction is allowed.",
    -1714: "Wrong keyword for a special function.",
    -1715: "The handler did not get all the required parameters.",
    -1716: "Unknown Apple event address type.",
    -1717: "No handler in the dispatch tables fits the supplied parameters.",
    -1718: "The contents of the reply you are accessing have not arrived yet.",
    -1719: "The index is out of range in a put operation.",
    -900: "The PPC Toolbox has not been initialized.",
    -902: "Invalid or inappropriate locationKindSelector in the location name.",
    -903: "Invalid port name. Unable to open the port or bad portRefNum.",
    -904: "The system is unable to allocate memory. This is a critical error, restart the machine.",
    -905: "Network activity is currently disabled.",
    -906: "The port does not exist at the destination.",
    -907: "The PPC Toolbox is unable to create a session.",
    -908: "Invalid session reference number.",
    -909: "Bad parameter or invalid state for this operation.",
    -910: "Another port is already open with this name.",
    -911: "The user name is unknown on the destination machine.",
    -912: "The destination rejected the session request.",
    -913: "The user has not named the Macintosh in the Network Setup Control Panel.",
    -914: "A system resource is missing.",
    -915: "Unable to contact the destination application.",
    -916: "The port was closed.",
    -917: "The session has closed.",
    -919: "The PPCPortRec is invalid.",
    -922: "The user has not specified an owner name in the Sharing Setup Control Panel.",
    -923: "The default userRefNum does not yet exist.",
    -924: "Unable to create a new userRefNum.",
    -925: "An error occurred in the network.",
    -926: "PPCStart failed because the destination did not have an inform pending.",
    -927: "The user password is wrong.",
    -928: "Invalid user reference number.",
    -930: "The service method is other than ppcServiceRealTime.",
    -931: "The location name is invalid.",
    -932: "The destination port requires authentication.",
    -1967390719: "The packet is too short or too long.",
    -1967390712: "Cannot resolve the name to a network address.",
    -1967390711: "The network operation timed out.",
    -1967390704: "The socket has been disconnected by its peer.",
    -1967390703: "Could not resolve the service to a port address.",
    -1967390702: "Timed out while trying to connect to the peer.",
    -1967390701: "Socket startup (WSAStartup) failed.",
    -1074003967: "Parameter 1 is out of range.",
    -90165: (
        "A command occurred that is only supported within a loop, such as a For Loop or a While "
        "Loop."
    ),
    14001: "Invalid refnum.",
    14002: "Invalid string.",
    14003: "The request for a synchronous advise transaction timed out.",
    14004: "The response set the DDE_FBUSY bit.",
    14005: "The request for a synchronous data transaction timed out.",
    14006: (
        "DDEML was called without first calling DdeInitialize, or was passed an invalid instance "
        "identifier."
    ),
    14007: "A monitor or client-only application attempted a DDE transaction.",
    14008: "The request for a synchronous execute transaction timed out.",
    14009: "A parameter was not validated by the DDEML.",
    14010: "The server application has outrun the client, consuming large amounts of memory.",
    14011: "A memory allocation failed.",
    14012: "The request or poke is for an invalid item.",
    14013: "The client conversation attempt failed.",
    14014: "The transaction failed.",
    14015: "The request for a synchronous poke transaction timed out.",
    14016: (
        "An application with a synchronous transaction in progress attempted to initiate another "
        "transaction."
    ),
    14017: (
        "A server-side transaction was attempted on a conversation terminated by the client, or "
        "the service terminated."
    ),
    14018: "Internal error in the DDEML.",
    14019: "The request to end advise timed out.",
    14020: "An invalid transaction identifier was passed to a DDEML function.",
}
