
from whatsapp_toolkit import devtools

# 1) Generate local templates (does NOT start Docker)
devtools.init_local_evolution(
    path=".",
    overwrite=True,
    verbose=True,
)

# 2) Control the local Evolution stack
stack = devtools.local_evolution(path=".")

# Start (foreground). Use detached=True for background.
stack.start(
    detached=False,
    build=True,
    verbose=True,
)

# Tail logs (Ctrl+C to stop)
stack.logs(follow=True)