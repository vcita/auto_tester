"""
Debug utilities for tests.

Use these when debugging with a human: pause before each step, print what is
about to happen, and wait for Enter so you can see exactly where a failure occurs.
"""

from typing import Callable


def step_callback_with_enter(msg: str) -> None:
    """
    Step callback that prints the next action and waits for Enter.

    Use as the step_callback argument in functions that support it (e.g.
    fn_delete_client, fn_delete_service). Before each minor action, the function
    will call this with a short message; this prints it and blocks on input(),
    so a human can see what is about to run and press Enter to continue.
    Helps pinpoint where an error or timeout occurs.

    Example:
        from tests.debug_utils import step_callback_with_enter
        fn_delete_client(page, context, step_callback=step_callback_with_enter)
    """
    print(f"\n  >>> ABOUT TO: {msg}")
    print("  >>> Press Enter to run this step...")
    input()


def make_step_callback_with_enter(
    prefix: str = "  >>> ",
    prompt: str = "Press Enter to run this step...",
) -> Callable[[str], None]:
    """
    Return a step callback that prints message and waits for Enter, with custom prefix/prompt.

    Use when you want different wording or logging format. Default is equivalent
    to step_callback_with_enter.

    Example:
        cb = make_step_callback_with_enter(prefix="[DEBUG] ")
        fn_delete_client(page, context, step_callback=cb)
    """
    def callback(msg: str) -> None:
        print(f"\n{prefix}ABOUT TO: {msg}")
        print(f"{prefix}{prompt}")
        input()
    return callback


__all__ = ["step_callback_with_enter", "make_step_callback_with_enter"]
