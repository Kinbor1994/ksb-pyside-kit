import click
import os
from pathlib import Path
import subprocess
from typing import Optional

class MigrationManager:
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = migrations_dir
        
    def init(self) -> bool:
        """Initialise alembic migrations"""
        try:
            result = subprocess.run(
                ["alembic", "init", self.migrations_dir], 
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            click.echo(click.style("Erreur lors de l'initialisation:", fg="red"))
            click.echo(click.style(f"Code de sortie: {e.returncode}", fg="yellow"))
            if e.stdout:
                click.echo(click.style("Sortie standard:", fg="yellow"))
                click.echo(e.stdout)
            if e.stderr:
                click.echo(click.style("Erreur standard:", fg="red"))
                click.echo(e.stderr)
            return False
            
    def create(self, message: str) -> Optional[str]:
        """Create a new migration"""
        try:
            result = subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", message],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            click.echo(click.style("Erreur lors de la création de la migration:", fg="red"))
            click.echo(click.style(f"Code de sortie: {e.returncode}", fg="yellow"))
            if e.stdout:
                click.echo(click.style("Sortie standard:", fg="yellow"))
                click.echo(e.stdout)
            if e.stderr:
                click.echo(click.style("Erreur standard:", fg="red"))
                click.echo(e.stderr)
            return None
            
    def upgrade(self, revision: str = "head") -> bool:
        """upgrade the database"""
        try:
            result = subprocess.run(
                ["alembic", "upgrade", revision],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            click.echo(click.style("Erreur lors de la mise à jour:", fg="red"))
            click.echo(click.style(f"Code de sortie: {e.returncode}", fg="yellow"))
            if e.stdout:
                click.echo(click.style("Sortie standard:", fg="yellow"))
                click.echo(e.stdout)
            if e.stderr:
                click.echo(click.style("Erreur standard:", fg="red"))
                click.echo(e.stderr)
            return False

    def downgrade(self, revision: str = "-1") -> bool:
        """Downgrade the database"""
        try:
            result = subprocess.run(
                ["alembic", "downgrade", revision],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            click.echo(click.style("Erreur lors du retour arrière:", fg="red"))
            click.echo(click.style(f"Code de sortie: {e.returncode}", fg="yellow"))
            if e.stdout:
                click.echo(click.style("Sortie standard:", fg="yellow"))
                click.echo(e.stdout)
            if e.stderr:
                click.echo(click.style("Erreur standard:", fg="red"))
                click.echo(e.stderr)
            return False
            
    def history(self) -> Optional[str]:
        """Show the migration history"""
        try:
            result = subprocess.run(
                ["alembic", "history"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            click.echo(click.style(f"Erreur lors de l'affichage de l'historique: {str(e)}", fg="red"))
            return None

@click.group()
def cli():
    """Management commands for Alembic migrations"""
    pass

@cli.command()
def init():
    """Initialise alembic migrations"""
    manager = MigrationManager()
    if manager.init():
        click.echo(click.style("Migrations initialisées avec succès!", fg="green"))

@cli.command()
@click.argument('message')
def create(message):
    """Create a new migration"""
    manager = MigrationManager()
    output = manager.create(message)
    if output:
        click.echo(click.style("Migration créée avec succès!", fg="green"))
        click.echo(output)

@cli.command()
@click.option('--revision', default='head', help='Révision cible (défaut: head)')
def upgrade(revision):
    """Upgrade the database"""
    manager = MigrationManager()
    if manager.upgrade(revision):
        click.echo(click.style("Base de données mise à jour avec succès!", fg="green"))

@cli.command()
@click.option('--revision', default='-1', help='Révision cible (défaut: -1)')
def downgrade(revision):
    """Downgrade the database"""
    manager = MigrationManager()
    if manager.downgrade(revision):
        click.echo(click.style("Retour arrière effectué avec succès!", fg="green"))

@cli.command()
def history():
    """show the migration history"""
    manager = MigrationManager()
    hist = manager.history()
    if hist:
        click.echo(hist)

if __name__ == '__main__':
    cli()