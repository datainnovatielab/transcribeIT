How to contribute to Nota Bene
==============================

Thank you for considering contributing to Nota Bene!


Support questions
-----------------

Please, don't use the issue tracker for this. The issue tracker is a
tool to address bugs and feature requests in Nota Bene itself.


Reporting issues
----------------

Issues can be reported at our
`issue tracker <https://gitlab.com/datainnovatielab/projects/nota-bene/-/issues>`__.
Include the following information in your post:

-   Describe what you expected to happen.
-   If possible, include a
    `minimal reproducible example <https://stackoverflow.com/help/minimal-reproducible-example>`__ to help us identify the issue. This also helps check that the issue is not with your own code.
-   Describe what actually happened. Include the full traceback if there
    was an exception.
-   List your Python, Nota Bene, and other relevant versions. If possible, check if this issue is already fixed in the latest Nota Bene release or the latest development version.


Submitting patches
------------------

If there is not an open issue at our
`issue tracker <https://gitlab.com/datainnovatielab/projects/nota-bene/-/issues>`__ for what you want to submit, prefer opening one for discussion before working on a PR.

When you start working on an issue, make sure to include the following in your patch:

-   Make sure your code passes the `pre-commit <https://pre-commit.com>`__
    checks. Install pre-commit using the instructions below.

-   Include tests if your patch adds or changes code. Make sure the test
    fails without your patch.
-   Update any relevant docs pages and docstrings.


Installing pre-commit and requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   Install Nota Bene in editable mode with development dependencies.

    .. code-block:: bash

        pip install '.[dev]'
        pip install .

-   Install the pre-commit hooks.

    .. code-block:: bash

        pre-commit install


Start coding
~~~~~~~~~~~~

-   Create a branch to identify the issue you would like to work on. If
    you're submitting a feature addition, change or non-critical bug fix,
    branch off of the "develop" branch.

    .. code-block:: bash

        git fetch origin
        git checkout -b your-branch-name origin/develop

-   Critical bug fixes should be branched off of the "main" branch instead.

    .. code-block:: bash

        git fetch origin
        git checkout -b your-branch-name origin/main

-   Link to the issue being addressed with
    ``fixes #123`` in the merge or pull request.


Building the docs
~~~~~~~~~~~~~~~~~

Build the docs in the ``docs`` directory using `Sphinx <https://www.sphinx-doc.org/en/stable/>`__.

.. code-block:: bash

    make --directory=docs html

Open ``docs/_build/html/index.html`` in your browser to view the docs.
