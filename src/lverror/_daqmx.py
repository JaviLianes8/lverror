"""Common NI-DAQmx error codes.

Compiled from public National Instruments documentation (the NI knowledge base article on
common NI-DAQmx error codes and a published NI-DAQmx driver error-code table). DAQmx defines
many thousands of codes; only commonly hit ones that are publicly documented are shipped here.
No message is invented.
"""

from __future__ import annotations

DAQMX: dict[int, str] = {
    -50103: (
        "The specified resource is reserved. The operation could not be completed as specified."
    ),
    -50251: "The specified software component is not available, or the component was not loaded.",
    -200019: (
        "The requested read offset could not be configured, so it was coerced to the minimum "
        "supported value."
    ),
    -200022: "A resource requested by this task has already been reserved by a different task.",
    -200041: "The destination terminal to be routed could not be found on the device.",
    -200077: (
        "The requested value is not a supported value for this property, possibly a conflict with "
        "another property."
    ),
    -200088: "The task specified is invalid or does not exist.",
    -200170: (
        "The physical channel specified does not exist on this device. Check the device "
        "documentation for available channels."
    ),
    -200172: "The buffer size must be zero when the data transfer mechanism is programmed I/O.",
    -200220: "The device identifier is invalid.",
    -200234: "The buffer is too small to fit the requested samples to write.",
    -200279: (
        "Attempted to read samples that are no longer available. The requested sample was "
        "previously available but has since been overwritten. Increase the buffer size, read more "
        "often, or read fewer samples."
    ),
    -200284: (
        "Some or all of the samples requested have not yet been acquired. Increase the read "
        "timeout or wait longer before reading."
    ),
    -200324: (
        "NI-DAQmx cannot communicate with the device. Confirm it is present, powered, not being "
        "reset, and not reserved by another driver."
    ),
    -200378: "The custom scale specified does not exist.",
    -200380: (
        "The strain gage calibration procedure failed. Check connections, bridge type, shunt "
        "resistor location, and jumpers."
    ),
    -200414: "The requested sample clock source is invalid.",
    -200428: (
        "The value passed to the Task/Channels In control is invalid, it must refer to a valid "
        "task or virtual channels."
    ),
    -200452: (
        "The specified property is not supported by the device or is not applicable to the task."
    ),
    -200462: (
        "Generation cannot start because the output buffer is empty. Write data before starting a "
        "buffered generation."
    ),
    -200477: "The specified operation cannot be performed when there are no devices in the task.",
    -200479: "The specified operation cannot be performed while the task is running.",
    -200489: (
        "The channel cannot be added because a channel with the same name is already in the task."
    ),
    -200520: (
        "The calibration constants stored in EEPROM are invalid. Perform a self or external "
        "calibration."
    ),
    -200524: (
        "The write failed because the number of channels in the data does not match the number in "
        "the task."
    ),
    -200545: (
        "Self-calibration failed to converge. Disconnect external signals and perform an external "
        "calibration."
    ),
    -200561: (
        "The analog data written is too large or too small for the channel range. Adjust the "
        "channel minimum and maximum."
    ),
    -200587: (
        "The requested operation failed because the specified digital lines are reserved, or the "
        "device is not present in NI-DAQmx."
    ),
    -200598: "A repeated number in Prescaled Values is invalid for input operations.",
    -200600: (
        "NI-DAQmx cannot generate virtual channel names because the numeric suffix would be too "
        "large."
    ),
    -200604: "A NULL pointer was passed for a required parameter.",
    -200608: (
        "Acquisition cannot start because the selected buffer size is too small. Increase the "
        "buffer size."
    ),
    -200609: (
        "Generation cannot start because the selected buffer size is too small. Increase the "
        "buffer size."
    ),
    -200621: (
        "Onboard device memory underflow because the driver could not write data fast enough for "
        "the output rate."
    ),
    -200982: "DAQmx Signal Events are not supported by your device.",
    -201003: "The device cannot be accessed. Ensure it is connected and powered, then restart.",
    -201100: (
        "A sample clock timebase divisor cannot be specified when an external sample clock source "
        "is used."
    ),
    -201395: "The task contains no channels or is not buffered.",
    -201435: "No samples were provided to initialize a buffered generation.",
    -209800: (
        "DAQmx Read did not finish before the next sample clock or change detection event arrived."
    ),
    -209801: "DAQmx Write did not finish before the next sample clock arrived.",
    -209802: (
        "One or more sample clocks were missed since the last Wait for Next Sample Clock call."
    ),
    -209803: "Three or more sample clocks were missed and data was lost.",
}
