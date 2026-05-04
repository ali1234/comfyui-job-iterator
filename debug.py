import sys
import os
import textwrap
import code

from .registry import register_node
from .types import Any, Variadic


class RestoreStdStreams(object):
    # ComfyUI-Manager patches sys.stdout and sys.stderr
    # which breaks GNU Readline support and makes the
    # REPL annoying to use. This context manager temporarily
    # puts back the originals.

    def __enter__(self):
        self._stdout, self._stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        self._stdout.flush(); self._stderr.flush()

    def __exit__(self, exc_type, exc_value, traceback):
        _stdout, _stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = self._stdout, self._stderr
        _stdout.flush(); _stderr.flush()


EOF = 'Ctrl-Z plus Return' if os.sep == '\\' else 'Ctrl-D (i.e. EOF)'
MESSAGE = f"Press {EOF} to continue processing."


class Quitter:
    # Replace exit() and quit() to make sure the user exits with EOF
    # otherwise the whole server gets terminated.

    def __repr__(self):
        return MESSAGE

    def __call__(self):
        print(MESSAGE)


@register_node(category='debug', output=True, display_name='Interact')
def Interact(inputs: Variadic(Any)) -> ():
    """Opens an interactive REPL whenever the node is evaluated."""
    if sys.__stdout__.isatty():
        with RestoreStdStreams():
            code.interact(
                banner=textwrap.dedent(f"""
                    Interactive debugging started.
                    inputs = {inputs!r}
                    {MESSAGE}
                """),
                exitmsg="Resuming workflow...",
                local={
                    'inputs': inputs,
                    'quit': Quitter(),
                    'exit': Quitter(),
                }
            )
    else:
        # Don't block the server if there is no tty.
        print("Skipping interactive prompt because there is no tty.")
    return ()

