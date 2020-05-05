======================================
Setting up the development environment
======================================

.. _check-your-installation:

Check your installation
=======================

Check your Python version
-------------------------
dynrat requires Python 3.7. To check your Python version, open a command prompt
and type the following command.

.. code-block:: winbatch

    >python --version

The output of the command will show the Python version. If the command fails,
or the version shown isn't 3.7, see :ref:`installing-python`.

Check for an IDE
----------------
If you are going to be editing code, it is recommended that you use an IDE. If
you don't plan on editing or viewing code, you may skip this step.

There is no requirement of which IDE to use, but if you aren't familiar with an
IDE, I recommend using Visual Studio Code (VSCode). To see if VSCode is
installed, you can either start search for it from the Windows Start menu, or
you can type the following command into the command prompt to start the
program.

.. code-block:: winbatch

    >code

If you're unable to locate VSCode on your system, see :ref:`installing-vscode`.

Check for a Git installation
----------------------------
You must have Git installed in order to clone the remote dynrat repository. To
see if Git is installed on your system, type the following command into a
command prompt.

.. code-block:: winbatch

    >git --version

This will display the version of Git installed on your system. If the command
fails, see :ref:`installing-git`.

.. _setup-clone-the-repo:

Clone the repository
====================
You must be connected to the DOI network to access projects on code.usgs.gov
through SSH.

First, make sure you can access repositories on code.usgs.gov through the SSH
protocol. To test your access, open Git Bash and type the following command.

.. code-block:: console

    $ ssh -T git@code.usgs.gov

If the above command prints a DOI warning banner, then `Welcome to GitLab` and
your user name, then you have SSH access on your system. If the command fails,
then see :ref:`setting-up-gitlab-ssh`.

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
    Python 3.7.7

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
