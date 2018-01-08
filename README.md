Stagger
=======
The Stagger block splits a list of signals into individual one-item lists and emits each one evenly over the configured period.

Properties
----------
- **min_interval**: If the number of signals and the *Period* would cause signals to emit more often than this time period, then group signals into lists with multiple items so that signals are emitted on this minimum interval.
- **period**: Time period to spread out the incoming signals.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signals split and emitted over the *Period*.

Commands
--------
None

Dependencies
------------
None

