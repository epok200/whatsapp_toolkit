import typer
from whatsapp_toolkit.cli.evolution import app as evolution_app
from whatsapp_toolkit.cli.webhook import app as webhook_app


app = typer.Typer(
    add_completion=False,
    help="WhatsApp Toolkit CLI: una potente herramienta para la automatización e integración de WhatsApp en Python.",
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)

app.add_typer(evolution_app, name="evo")
app.add_typer(webhook_app, name="webhook")


if __name__ == "__main__":
    app()
