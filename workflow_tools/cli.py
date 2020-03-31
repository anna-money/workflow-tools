import click

from .secret import Secret
from .template import env_to_namespace, get_secrets_from_template, get_user_variables_from_template, render_template

pass_secret = click.make_pass_decorator(Secret, ensure=True)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("input", required=False, type=click.File("r"))
@click.argument("output", required=False, type=click.File("w"))
@click.option("-p", "--prefix", default="WORKFLOW", help="Set prefix for envs to be used in template interpolation")
@click.option("-e", "--envfile", type=click.File("r"), help="Load env from file. OS envs overwrite file values")
@click.option("--secrets/--no-secrets", default=False, help="Show only secrets needed for the workflow")
@click.option("--vars/--no-vars", default=False, help="Show only user defined variables needed for the workflow")
@click.option("--strict/--no-strict", default=True, help="Throw exceptions for undefined variables")
def generator(input, output, prefix, envfile, secrets, vars, strict):
    """
    GitHub Workflow Generator based on Jinja2 templates.

    Interpolate Jinja2 template from INPUT with environment variables and write to OUTPUT.

    Template variables to be interpolated in the template should be denoted as follows:

    [[ workflow.your_variable ]]

    INPUT and OUTPUT can be files or standard input and output respectively.
    With no INPUT, or when INPUT is -, read standard input.
    With no OUTPUT, or when OUTPUT is -, write to standard output.

    EXAMPLES

    1. Common patterns working with input/output

      workflow_generator input.tmpl output.yaml

      workflow_generator - output.yaml

      workflow_generator input.tmpl -

      workflow_generator input.tmpl

      tail -n 12 input.tmpl | workflow_generator > output.yaml

    2. Generate Pull Request GitHub workflow with the values taken from the envfile

      workflow_generator YOUR-TEMPLATES-PATH/pr.tmpl YOUR-WORKFLOWS-PATH/pr.yml -e YOUR-TEMPLATES-PATH/.env.example

    3. Override values from envfile by the environment variable

      WORKFLOW_PROJECT=test workflow_generator YOUR-TEMPLATES-PATH/pr.tmpl -e YOUR-TEMPLATES-PATH/.env.example
    """
    stream_in = input or click.get_text_stream("stdin")
    stream_out = output or click.get_text_stream("stdout")
    strictness = strict and (not vars) and (not secrets)

    namespace = env_to_namespace(prefix=prefix, stream=envfile or None)
    template = render_template(stream=stream_in, strict=strictness, prefix=prefix, namespace=namespace, dry_run=vars)

    if vars:
        click.echo(get_user_variables_from_template(rendered_template=template, prefix=prefix))
        return

    if secrets:
        click.echo(get_secrets_from_template(template))
        return

    click.echo(message=template, file=stream_out)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--owner", help="Repository owner")
@click.option("--repo", help="Repository name")
@click.option("--token", help="GitHub access token")
@click.option("--debug/--no-debug", default=False, help="Log debug information")
@click.pass_context
def secret(ctx, owner, repo, token, debug):
    """
    Create, update or list GitHub secrets for the repository

    EXAMPLES

    Let's work with the repository https://github.com/anna-money/workflow-tools

    1. Create a secret HELLO=WORLD

      workflow_secret --owner=anna-money --repo=workflow-tools --token="account:token" \
        --debug update --key=HELLO --value=WORLD

    2. Get a list of all secrets

      workflow_secret --owner=anna-money --repo=workflow-tools --token="account:token" list

    3. Get info about a secret

      workflow_secret --owner=anna-money --repo=workflow-tools --token="account:token" get --key HELLO

    4. Delete a secret HELLO

      workflow_secret --owner=anna-money --repo=workflow-tools --token="account:token" delete --key HELLO
    """
    ctx.obj = Secret(owner, repo, token, debug)


@secret.command()
@click.option("--key", help="GitHub Secret Name")
@pass_secret
def get(secret, key):
    """
    Check details of secret
    """
    result = secret.get(key)
    click.echo(result)


@secret.command()
@pass_secret
def list(secret):
    """
    List all secrets for the repository
    """
    result = secret.list()
    click.echo(result)


@secret.command()
@click.option("--key", help="GitHub Secret Name")
@click.option("--value", help="GitHub Secret Value")
@pass_secret
def update(secret, key, value):
    """
    Create or update secret in the repository
    """
    result = secret.update(key, value)
    click.echo(result)


@secret.command()
@click.option("--key", help="GitHub Secret Name")
@pass_secret
def delete(secret, key):
    """
    Delete secret
    """
    result = secret.delete(key)
    click.echo(result)
