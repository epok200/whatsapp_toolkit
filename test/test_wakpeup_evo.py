from whatsapp_toolkit import devtools

devtools.init_local_evolution(
    path=".",        # carpeta actual
    overwrite=True,
    verbose=True
)



stack = devtools.local_evolution(path=".")

stack.start(
    detached=False,  # True = background
    build=True,
    verbose=True
)


stack.logs()                # todos
stack.logs("evolution-api") # solo servicio