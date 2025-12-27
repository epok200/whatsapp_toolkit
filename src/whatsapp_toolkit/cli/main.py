import typer
from whatsapp_toolkit.cli.evolution import app as evolution_app



app = typer.Typer(
    add_completion=False,
    help="WhatsApp Toolkit CLI - A powerful toolkit for WhatsApp automation and integration in Python.",
)

app.add_typer(evolution_app, name="evo")



if __name__ == "__main__":
    app()


