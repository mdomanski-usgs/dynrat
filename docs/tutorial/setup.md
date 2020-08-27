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
If you are going to be editing code, it is generally recommended that you use
an IDE. If you don't plan on editing or viewing code, you may skip this step.

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

## Clone the repositories
When you clone a repository, you tell the Git client on your local machine to
make a copy of and track changes in a remote Git repository. In this case, the
remote repositories you will be cloning are hosted on code.usgs.gov.

You must be connected to the DOI network to access projects on code.usgs.gov
through SSH.

### Check your SSH access
First, make sure you can access repositories on code.usgs.gov through the SSH
protocol. To test your access, open Git Bash and type the following command.

```
$ ssh -T git@code.usgs.gov
```

If the above command prints a DOI warning banner, then `Welcome to GitLab` and
your user name, then you have SSH access on your system. As an example, the
output after I run the command is shown below.

```
#============================================================================#
                        WARNING TO USERS OF THIS SYSTEM

This computer system, including all related equipment, networks, and network
devices (including Internet access), is provided by the Department of the
Interior (DOI) in accordance with the agency policy for official use and
limited personal use.
All agency computer systems may be monitored for all lawful purposes,
including but not limited to, ensuring that use is authorized, for management
of the system, to facilitate protection against unauthorized access, and to
verify security procedures, survivability and operational security. Any
information on this computer system may be examined, recorded, copied and
used for authorized purposes at any time.
All information, including personal information, placed or sent over this
system may be monitored, and users of this system are reminded that such
monitoring does occur. Therefore, there should be no expectation of privacy
with respect to use of this system.
By logging into this agency computer system, you acknowledge and consent to
the monitoring of this system. Evidence of your use, authorized or
unauthorized, collected during monitoring may be used for civil, criminal,
administrative, or other adverse action. Unauthorized or illegal use may
subject you to prosecution.
#============================================================================#

Welcome to GitLab, @mdomanski!
```

If the command fails,
see [Setting up GitLab SSH](ssh.md).

### Clone the anchovy and dynrat repositories
anchovy contains functionality to compute cross section geometry and is a
dependency of dynrat. At this time, the best way to obtain anchovy is to clone
the repository.

In Git Bash, navigate to the directory where you want to store the
repositories. When you clone a repository, an new directory with the name of
the project will be created, and the directory will contain the repository. To
clone the dynrat repository, type the following command.

```
$ git clone git@code.usgs.gov:dynamic-rating/dynrat.git
```

The following command clones the anchovy repository.

```
$ git clone git@code.usgs.gov:mdomanski/aluminiumanchovy.git
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

You must activate the virtual environment when you work with the dynrat package
in the future. If you work with VSCode, the IDE will activate the environment
in the terminal after the Python extension is loaded and a new terminal is
opened.

### Install anchovy
In order for the Python interpreter in the dynrat environment to have "global"
access to the anchovy package, you'll have to install the package within the
dynrat environment.

This command assumes you're working in the dynrat directory and have cloned the
anchovy repository in the parent directory.

```
(env) $ pip install -e ../aluminumanchovy
```

The `-e` option tells pip to install the anchovy package in "editable" mode.
See [Editable installs](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) for more info. `../aluminumanchovy` tells pip to look for a `setup.py` file in
the directory named aluminumanchovy which is one level above the current
working directory. The `setup.py` file tells pip what to install, among other
things.

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

If you get an `SSLError` when trying to install the requirements, this is most
likely due to pip not being able to resolve the DOI SSL intercept. If you're on
the DOI network or want to be connected to the DOI VPN when running the
command, see [DOI SSL Intercept](pip-ssl.md) and try again. Otherwise, if
you're teleworking and connected to the DOI VPN, try disconnecting and running
the command again.

### Install the IPython kernel
**This step may be skipped if you're going to be working with notebooks within
VSCode.**

This command installs the ipython kernel in your user profile. This makes the
kernel visible to the Jupyter Notebook server.

```
(env) $ python -m ipykernel install --user --name dynratenv --display-name "Python (dynrat)"
```

See more at
[Installing the IPython kernel](https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments)

### Install the dynrat package
Similar to the anchovy package, you will install the dynrat package in the
dynrat environment using the editable option.

This command assumes your current working directory is the directory that
contains the dynrat repository.

```
(env) $ pip install -e .
```

### Build the documentation (optional)
This command creates HTML documentation from the reStructuredText files within
the repository.

```
(env) $ python setup.py build_sphinx
```

The HTML documentation will be available in docs/_build/html directory. The
starting page is index.html. This tutorial is included in the documentation and
will be rendered as HTML.

### Run the unit test suite (optional)
```
(env) $ python setup.py test
```
