# Setting up the development environment

## Check your installation

### Check your Python version
dynrat requires Python 3.7. To check your Python version, open a command prompt
and type the following command.

```
>python --version
```

The output of the command will show the Python version. If the command fails,
or the version shown isn't 3.7, see [Installing python](install.md#installing-python).

### Check for an IDE
If you are going to be editing code, it is recommended that you use an IDE. If
you don't plan on editing or viewing code, you may skip this step.

There is no requirement of which IDE to use, but if you aren't familiar with an
IDE, I recommend using Visual Studio Code (VSCode). To see if VSCode is
installed, you can either start search for it from the Windows Start menu, or
you can type the following command into the command prompt to start the
program.

```
>code
```

If you're unable to locate VSCode on your system, see
[Installing Visual Studio Code](install.md#installing-visual-studio-code).

### Check for a Git installation
You must have Git installed in order to clone the remote dynrat repository. To
see if Git is installed on your system, type the following command into a
command prompt.

```
>git --version
```

This will display the version of Git installed on your system. If the command
fails, see [Installing Git](install.md#installing-git).

## Clone dynrat
You must be connected to the DOI network to access projects on code.usgs.gov
through SSH.

### Check your SSH access
First, make sure you can access repositories on code.usgs.gov through the SSH
protocol. To test your access, open Git Bash and type the following command.

```
$ ssh -T git@code.usgs.gov
```

If the above command prints a DOI warning banner, then `Welcome to GitLab` and
your user name, then you have SSH access on your system. If the command fails,
then see [Setting up GitLab SSH](ssh).

### Clone the repository
In Git Bash, navigate to the directory where you want to store the repository.
When you clone a repository, an new directory with the name of the project
will be created, and the directory will contain the repository. To clone the
dynrat repository, type the following command.

```
$ git clone git@code.usgs.gov:dynamic-rating/dynrat.git
```

### Change directories
Before you continue, change directories into the dynrat directory by typing the
following command.

```
$ cd dynrat
```

## Set up a virtual environment
In creating a virtual environment, you will create an isolated installation of
Python and install the supporting packages with the correct versions. The
environment will be created within the dynrat directory and it will stand apart
from other Python environments on your machine.

### Create a virtual environment
Create an environment using the venv module.

```
$ python -m venv env
```

See the [Virtual Environments and Packages](https://docs.python.org/3.7/tutorial/venv.html) and
[venv](https://docs.python.org/3.7/library/venv.html) documentation for more
information.

### Activate the virtual environment
Use the `activate` command to activate the virtual environment. The name of the
environment will appear in parentheses in the shell prompt. To activate the
environment in the Git Bash terminal, type the following command.

```
$ . env/Scripts/activate
(env) $
```

To activate the virtual environment in the Windows command prompt (outside of
this tutorial, for instance), type the following command

```
>env\Scripts\activate
```

After setting up the virtual environment, you must activate it when you work
with the dynrat package in the future.

### Install the required packages
In the dynrat repository, there is a file named `requirements.txt` that
contains a list of Python packages that are required by dynrat. The
requirements file is used with pip (the standard Python package management
system) to install the required packages in the new environment.

Type the following command to install the required packages in the new
environment.

```
(env) $ pip install -r requirements.txt
```

If you get an `SSLError` when trying to install the requirements, see
[DOI SSL Intercept](pip-ssl) and try again.

### Install the IPython kernel
```
(env) $ python -m ipykernel install --user --name dynratenv --display-name "Python (dynrat)"
```

See more at
[Installing the IPython kernel](https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments)

### Install the dynrat package
In order for the Python interpreter in the dynrat environment to have "global"
access to the dynrat package, you'll have to install the package within the
dynrat environment.

```
(env) $ pip install -e .
```

The `-e` option tells pip to install the dynrat package in "editable" mode.
See [Editable installs](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) for more info.


Build the documentation (optional)
----------------------------------
```
(env) $ python setup.py build_sphinx
```
