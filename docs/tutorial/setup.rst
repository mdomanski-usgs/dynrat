======================================
Setting up the development environment
======================================

All commands are for Bash (or Git Bash)

Clone the repository
====================
.. code-block:: console

    $ git clone git@code.usgs.gov:dynamic-rating/dynrat.git

Change directories
==================
.. code-block:: console

    $ cd dynrat

Create a virtual environment
============================
dynrat has only been tested with Python version 3.7. To make sure you're
creating an environment with the correct version, use the following command.

.. code-block:: console

    $ python --version
    Python 3.7.5

Create an environment using the venv module.

.. code-block:: console

    $ python -m venv env

See the `Virtual Environments and Packages <https://docs.python.org/3.7/
tutorial/venv.html>`_ and `venv documentation <https://docs.python.org/3.7/
library/venv.html>`_ for more information.

Activate the virtual environment
================================
Use the `activate` command to activate the virtual environment. The name of the
environment will appear in parentheses in the shell prompt.

.. code-block:: console

    $ . env/Scripts/activate
    (env) $

Install the required packages
=============================
.. code-block:: console

    (env) $ pip install -r requirements.txt

Install the IPython kernel
==========================
.. code-block:: console

    (env) $ python -m ipykernel install --user --name dynratenv --display-name "Python (dynrat)"

See more at
`Installing the IPython kernel <https://ipython.readthedocs.io/en/stable/
install/kernel_install.html#kernels-for-different-environments>`_

Install the dynrat package
==========================

In order for the Python interpreter in the dynrat environment to have "global"
access to the dynrat package, you'll have to install the package within the
dynrat environment.

.. code-block:: console

    (env) $ pip install -e .

The -e option tells pip to install the fluegg package in "editable" mode.
See `Editable installs <https://pip.pypa.io/en/stable/reference/pip_install/
#editable-installs>`_ for more info.


Build the documentation (optional)
==================================

.. code-block:: console

    (env) $ python setup.py build_sphinx
