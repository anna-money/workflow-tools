workflow-tools
==============

|Build| |Black| |License|

.. raw:: html

   <img align="right" src="https://github.com/anna-money/workflow-tools/blob/master/docs/_static/workflow-tools-transparent-thumbnail.png">

CLI tools for GitHub Actions.

- Automate writing GitHub workflow configs with a generator tool
- Automate setting GitHub secrets for repositories
- Integrate the tools into your pipeline for setting up new microservices


Rationale
---------

Microservice architecture may have dozens and dozens of lookalikes services that require similar CI/CD workflows.
With infrastructure as code approach taken by the `GitHub Actions`_, why not using workflows generation?
Setting up a new microservice repository may also be automated. This is where ``workflow-tools`` come in handy.


Examples
--------

Let's set `GitHub Secrets`_ for a repository. First, get a `personal access token`_ in GitHub settings.
Then set up a secret using ``workflow-tools``:

.. code-block:: bash

  workflow_secret --owner=anna-money --repo=workflow-tools \
    --token="YOUR-PERSONAL-ACCESS-TOKEN" \
    update --key=MY_SECRET_KEY --value=MY_VALUE

Now let's use a fragment of `Jinja2`_ template for a GitHub Actions workflow to generate resulting config:

.. code-block:: bash

  WORKFLOW_RUNNER_VERSION=ubuntu-18.04 WORKFLOW_PYTHON27=2.7 WORKFLOW_PYTHON37=3.7 \
  workflow_generator
  # Press Enter to start pasting Jinja2 workflow template into stdin
  jobs:
    test:
      runs-on: [[ workflow.runner_version ]]
      strategy:
        matrix:
          python:
            - [[ workflow.python27 ]]
            - [[ workflow.python37 ]]
  # Press Ctrl+D to render resulting workflow
  # For real workflow templates use reading/writing from/to a file, load variables from envfile
  jobs:
    test:
      runs-on: ubuntu-18.04
      strategy:
        matrix:
          python:
            - 2.7
            - 3.7


Help
----

See `documentation`_ for more details. Use ``--help`` flag for each tool in the package.


Installation
------------

Just run:

.. code-block:: bash

  pip install -U workflow-tools


Contributing
------------

See `CONTRIBUTING.rst`_.

.. |Build| image:: https://github.com/anna-money/workflow-tools/workflows/master/badge.svg
   :target: https://github.com/anna-money/workflow-tools/actions?query=workflow%3Amaster
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black
   :alt: Black Formatter
.. |License| image:: https://img.shields.io/github/license/anna-money/workflow-tools.svg
   :alt: GitHub License

.. _GitHub Actions: https://help.github.com/en/actions
.. _GitHub Secrets: https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets
.. _personal access token: https://github.com/settings/tokens
.. _Jinja2: https://jinja.palletsprojects.com/
.. _documentation: https://workflow-tools.readthedocs.io/
.. _CONTRIBUTING.rst: https://github.com/anna-money/workflow-tools/tree/master/CONTRIBUTING.rst
