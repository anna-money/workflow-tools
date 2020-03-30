import sys

import pytest

from workflow_tools.template import (
    _string_to_dict,
    env_to_namespace,
    get_secrets_from_template,
    get_user_variables_from_template,
)

if sys.version_info < (3, 3):
    from mock import patch
else:
    from unittest.mock import patch


@pytest.mark.parametrize(
    "input_string, expected_result",
    [("hello=world\ntest=me", {"hello": "world", "test": "me"}), ("test me", {}), ("", {})],
)
def test_string_to_dict(input_string, expected_result):
    actual_result = _string_to_dict(input_string)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "rendered_template, prefix, expected_result",
    [
        ("something: [[ test.whatever ]]", "TEST", {"TEST_WHATEVER"}),
        ("something: [[ test.whatever ]]", "TEST___", {"TEST_WHATEVER"}),
        ("something: [[ test.whatever ]]", "WORKFLOW", set()),
    ],
)
def test_get_user_variables_from_template(rendered_template, prefix, expected_result):
    actual_result = get_user_variables_from_template(rendered_template, prefix)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "rendered_template, expected_result",
    [
        ("something: ${{ secrets.whatever }}", {"whatever"}),
        ("something: {{ secrets.whatever }}", set()),
        ("something: [[ test.whatever ]]", set()),
    ],
)
def test_get_secrets_from_template(rendered_template, expected_result):
    actual_result = get_secrets_from_template(rendered_template)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "prefix, environ, expected_result",
    [
        ("WORKFLOW_TEST", {"WORKFLOW_TEST_SOMETHING": "me"}, {"something": "me"}),
        ("ANOTHER_PREFIX", {"WORKFLOW_TEST_SOMETHING": "me"}, {}),
        ("ANOTHER_PREFIX", {}, {}),
    ],
)
def test_env_to_namespace(prefix, environ, expected_result):
    with patch.dict("workflow_tools.template.os.environ", values=environ):
        actual_result = env_to_namespace(prefix=prefix)
        assert actual_result == expected_result
