import click
from ..authentication.controllers.user_controller import AuthController, PasswordValidationError
from ..authentication.models.user_model import UserType
from getpass import getpass

@click.group()
def cli():
    """CLI tools for user management"""
    pass

@cli.command()
@click.option('--username', prompt='Username', help='Username for the new user')
@click.option('--email', prompt='Email', help='Email address')
@click.option('--first-name', prompt='First name', help='First name')
@click.option('--last-name', prompt='Last name', help='Last name')
def create_user(username, email, first_name, last_name):
    """Create a new regular user"""
    try:
        # Get password securely
        while True:
            password = getpass('Password: ')
            password_confirm = getpass('Confirm password: ')
            
            if password == password_confirm:
                break
            click.echo('Passwords do not match. Please try again.')

        # Get secret question and answer
        click.echo('\nAvailable security questions:')
        questions = [
            "What was your first pet name?",
            "What city were you born in?",
            "What is your mother's maiden name?",
            "What is your favorite movie?"
        ]
        for idx, question in enumerate(questions, 1):
            click.echo(f"{idx}. {question}")
        
        question_idx = click.prompt('Select a security question (1-4)', type=int)
        if not 1 <= question_idx <= len(questions):
            raise click.BadParameter('Invalid question number')
            
        secret_question = questions[question_idx - 1]
        secret_answer = click.prompt('Your answer', hide_input=True)

        # Create user
        auth_controller = AuthController()
        user = auth_controller.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            secret_question=secret_question,
            secret_answer=secret_answer,
            user_type=UserType.DEFAULT
        )
        
        if user:
            click.echo(click.style('User created successfully!', fg='green'))
        else:
            click.echo(click.style('Failed to create user. Username or email might already exist.', fg='red'))
            
    except PasswordValidationError as e:
        click.echo(click.style(f'Password validation failed: {str(e)}', fg='red'))
    except Exception as e:
        click.echo(click.style(f'An error occurred: {str(e)}', fg='red'))

@cli.command()
@click.option('--username', prompt='Username', help='Username for the new superuser')
@click.option('--email', prompt='Email', help='Email address')
@click.option('--first-name', prompt='First name', help='First name')
@click.option('--last-name', prompt='Last name', help='Last name')
def create_superuser(username, email, first_name, last_name):
    """Create a new superuser (admin)"""
    try:
        # Get password securely
        while True:
            password = getpass('Password: ')
            password_confirm = getpass('Confirm password: ')
            
            if password == password_confirm:
                break
            click.echo('Passwords do not match. Please try again.')

        # Get secret question and answer
        click.echo('\nAvailable security questions:')
        questions = [
            "What was your first pet name?",
            "What city were you born in?",
            "What is your mother's maiden name?",
            "What is your favorite movie?"
        ]
        for idx, question in enumerate(questions, 1):
            click.echo(f"{idx}. {question}")
        
        question_idx = click.prompt('Select a security question (1-4)', type=int)
        if not 1 <= question_idx <= len(questions):
            raise click.BadParameter('Invalid question number')
            
        secret_question = questions[question_idx - 1]
        secret_answer = click.prompt('Your answer', hide_input=True)

        # Create superuser
        auth_controller = AuthController()
        user = auth_controller.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            secret_question=secret_question,
            secret_answer=secret_answer,
            user_type=UserType.ADMIN
        )
        
        if user:
            click.echo(click.style('Superuser created successfully!', fg='green'))
        else:
            click.echo(click.style('Failed to create superuser. Username or email might already exist.', fg='red'))
            
    except PasswordValidationError as e:
        click.echo(click.style(f'Password validation failed: {str(e)}', fg='red'))
    except Exception as e:
        click.echo(click.style(f'An error occurred: {str(e)}', fg='red'))

if __name__ == '__main__':
    cli()