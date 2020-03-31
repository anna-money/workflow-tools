.. _examples-docs:

Examples
========

Let's consider a real life example: setting up a GitHub Actions workflow for the `workflow-tools`_ repository itself.
We need:

1. Generate a GitHub Action workflow using ``workflow_generator`` tool
2. Set GitHub Secrets the workflow needs using ``workflow_secret`` tool

Generating workflow
-------------------

.. code-block:: bash
   :linenos:

   WORKFLOW_RUNNER_VERSION=ubuntu-latest \
   workflow_generator \
   docs/examples/master.tmpl \
   ~/PATH-TO-YOUR-REPO/.github/workflows/master.yml \
   -e docs/examples/envfile

First, we define a Jinja2-template for the workflow (see a :download:`file <examples/master.tmpl>` at line 3).
Variables to be substituted should be marked up this way:

.. code-block::

  [[ workflow.your_variable ]]

When rendering the resulting file, ``workflow-generator`` tool substitutes the markup with the value
of corresponding environment variable:

.. code-block::

   WORKFLOW_YOUR_VARIABLE


The environment variable can be set globally, for a single command run,
or can be read from the envfile specified by the option flag ``-e``
(see a :download:`file <examples/envfile>` at line 5).

Envfile comes in handy when a template uses many variables at once. It's also easier to share variables
between the templates using envfile. The envfile has the *lowest precedence*, it can be overridden (line 1).


Setting secrets
---------------

Now that we generated the workflow, let's set a GitHub secret used by the template:

.. code-block:: bash
   :linenos:

   workflow_secret \
     --owner=anna-money \
     --repo=workflow-tools \
     --token="YOUR-PERSONAL-ACCESS-TOKEN" \
    update \
      --key=PYPI_PUSH_USER \
      --value=YOUR_SECRET_VALUE

First, we need to get a `personal access token`_ (see line 4). ``workflow_secret`` tool has multiple commands
(see :ref:`tools-docs`). To set up new or update existing secret ``update`` command is used (line 5).
The command accepts ``--key`` and ``--value`` options (lines 6, 7). ``workflow_secret`` also have tool-wide
options used for each command: ``--owner`` (GitHub user, line 2), ``--repo`` (GitHub repository name, line 3) and
``--token``.

Finally, let's check what secrets are set for the repository:

.. code-block:: bash
   :linenos:

   workflow_secret \
     --owner=anna-money \
     --repo=workflow-tools \
     --token="YOUR-PERSONAL-ACCESS-TOKEN" \
    list


.. _workflow-tools: https://github.com/anna-money/workflow-tools
.. _personal access token: https://github.com/settings/tokens