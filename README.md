Stagger
=======

Stagger the notification of incoming signals over a period of time.

This block is often useful after a block like the [Queue](https://github.com/nio-blocks/queue) block that emits signals in groups. If, for visualization purposes, you don't want to see the chunks that another block notifies, you can place a stagger block after it and it will "smooth" out the delivery of signals.

Properties
--------------

-   **period**: Period of time over which to emit signals

Dependencies
----------------

None

Commands
----------------
None

Input
-------
Any group/list of signals

Output
---------
The same signals, only one-by-one, and in a staggered fashion. All incoming signals are guaranteed to be notified out of this block.
