from whatsapp_toolkit import devtools


devtools.init_local_evolution(
    path=".",
    overwrite=True,
    verbose=True,
)


stack = devtools.local_evolution(path=".")

stack.start(
    detached=False,
    build=True,
    verbose=True,
)

stack.logs(follow=True)