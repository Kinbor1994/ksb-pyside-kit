import click
import os
from pathlib import Path

TEMPLATE_FILES = {
    'models.py': '''# filepath: {app_path}/models.py
from ksb_pyside_kit.models import BaseModel

class {app_name_title}Model(BaseModel):
    pass
''',

    'controllers.py': '''# filepath: {app_path}/controllers.py
from ksb_pyside_kit.controllers.base_controller import BaseController
from .models import {app_name_title}Model

class {app_name_title}Controller(BaseController):
    def __init__(self):
        super().__init__({app_name_title}Model)
''',

    'forms.py': '''# filepath: {app_path}/forms.py

''',

    'pages.py': '''# filepath: {app_path}/pages.py
from ksb_pyside_kit.components import Page
''',

    '__init__.py': ''
}

@click.group()
def cli():
    """CLI pour la gestion des applications"""
    pass

@cli.command()
@click.argument('app_name')
def create_app(app_name):
    """Create an application"""
    click.echo(click.style(f'Création de l\'application: {app_name}', fg='blue'))
    try:
        # Normalise the app name
        app_name = app_name.lower().replace('-', '_')
        app_name_title = ''.join(word.title() for word in app_name.split('_'))
        
        # projet base directory
        base_dir = Path(os.getcwd())
        app_dir = base_dir / app_name
        app_path = str(app_dir).replace('\\', '/')

        # Check if the app already exists
        if app_dir.exists():
            click.echo(click.style(f'Une application nommée "{app_name}" existe déjà.', fg='red'))
            return

        # Create the application directory
        app_dir.mkdir(parents=True, exist_ok=True)
        click.echo(click.style(f'Création du dossier: {app_dir}', fg='green'))

        # Create app files
        for filename, template in TEMPLATE_FILES.items():
            file_path = app_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template.format(
                    app_name=app_name,
                    app_name_title=app_name_title,
                    app_path=app_path
                ))
            click.echo(click.style(f'Création du fichier: {file_path}', fg='green'))

        click.echo(click.style(f'\nApplication {app_name} créée avec succès !', fg='green'))
        click.echo('\nStructure créée :')
        click.echo(f"""
{app_name}/
├── __init__.py
├── models.py
├── controllers.py
├── forms.py
└── pages.py
""")

    except Exception as e:
        click.echo(click.style(f'Une erreur est survenue: {str(e)}', fg='red'))

@cli.command()
@click.argument('app_name')
def delete_app(app_name):
    """Delete an application"""
    try:
        app_dir = Path(os.getcwd()) / app_name

        if not app_dir.exists():
            click.echo(click.style(f"L'application {app_name} n'existe pas.", fg='red'))
            return

        if click.confirm(f'Êtes-vous sûr de vouloir supprimer l\'application {app_name} ?', abort=True):
            import shutil
            shutil.rmtree(app_dir)
            click.echo(click.style(f'Application {app_name} supprimée avec succès !', fg='green'))

    except Exception as e:
        click.echo(click.style(f'Une erreur est survenue: {str(e)}', fg='red'))

if __name__ == '__main__':
    cli()