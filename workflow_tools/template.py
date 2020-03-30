import os
import re
import shlex

import jinja2

from .const import JINJA_AUTOESCAPE, JINJA_DRY_RUN_VAR_END, JINJA_DRY_RUN_VAR_START, JINJA_VAR_END, JINJA_VAR_START

SECRET_REGEX = re.compile(r"\$\{\{ secrets\.(.*) \}\}")


def render_template(stream, strict, prefix, namespace, dry_run=False):
    data = stream.read()
    undefined = jinja2.StrictUndefined if strict else jinja2.Undefined
    var_start = JINJA_DRY_RUN_VAR_START if dry_run else JINJA_VAR_START
    var_end = JINJA_DRY_RUN_VAR_END if dry_run else JINJA_VAR_END
    template = jinja2.Template(
        source=data,
        autoescape=jinja2.select_autoescape(JINJA_AUTOESCAPE),
        undefined=undefined,
        variable_start_string=var_start,
        variable_end_string=var_end,
    )
    refined_prefix = prefix.rstrip("_").lower()
    kwargs = {refined_prefix: namespace}
    try:
        result = template.render(kwargs)
    except jinja2.exceptions.UndefinedError as exc:
        return "Variable is not defined: {}".format(exc)
    return result


def get_secrets_from_template(rendered_template):
    return set(re.findall(SECRET_REGEX, rendered_template))


def get_user_variables_from_template(rendered_template, prefix):
    refined_prefix = prefix.rstrip("_").lower()
    regex = r"\[\[ {}\.(.*) \]\]".format(refined_prefix)
    result = re.findall(regex, rendered_template)
    return {"{}_{}".format(refined_prefix.upper(), s.upper()) for s in result}


def _string_to_dict(data):
    result = {}
    for token in shlex.split(data):
        kv = token.split("=")
        if len(kv) == 2:
            result[kv[0]] = kv[1]
    return result


def env_to_namespace(prefix, stream=None):
    """
    Read environment variables with the prefix, convert them to match template variables

    If envs passed in as envfile, OS envs will override overlapping variables
    """
    envs = {}
    result = {}
    prefix = "{}_".format(prefix.rstrip("_"))

    if stream:
        envs.update(_string_to_dict(data=stream.read()))

    envs.update(os.environ)

    for e in envs:
        if e.startswith(prefix):
            key = e[len(prefix) :].lower()
            value = envs[e]
            result[key] = value
    return result
