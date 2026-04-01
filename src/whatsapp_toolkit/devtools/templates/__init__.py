from jinja2 import Environment, PackageLoader, StrictUndefined

_env = Environment(
    loader=PackageLoader("whatsapp_toolkit.devtools", "templates"),
    keep_trailing_newline=True,
    undefined=StrictUndefined,
)


def render_template(stack: str, name: str, **context: str) -> str:
    """Renderiza un template .j2 de un stack dado con las variables de contexto."""
    template = _env.get_template(f"{stack}/{name}")
    return template.render(**context)
