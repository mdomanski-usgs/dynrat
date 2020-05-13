# Installing required programs

## Installing Python
This assumes you'll be installing a new Python 3.7 environment as the primary
Python environment on your machine. Following these steps may cause you trouble
if other applications on your machine depend on a particular system-wide
version of Python. There are other options, but are not covered here.

### Download Python
Go to the [Python downloads page][1] and download the installer for the latest
release of the Python 3.7. As of this writing, the latest version is 3.7.7.

### Install Python
Run the installer. You may install Python using the "Just me" option if you
don't have admin rights on your machine. Be sure to mark the option to include
this installed version on PATH.

### Test the Python install
To be sure you have Python 3.7 up and running, open up a Command Prompt and
type in the following line. After installing the environment in this section of
the tutorial, you should get similar output as shown below.

```
>python --version
Python 3.7.7
```

Return to [Check your installation][4].

## Installing Visual Studio Code
Visual Studio Code (VSCode), not to be confused with Visual Studio, is a
lightweight, open source IDE developed and released by Microsoft. If you're
comfortable with and prefer other IDEs, you may skip this section.

### Download VSCode
Go to the [Visual Studio Code download page][2] and download the latest version
of VSCode.

### Install VSCode
Run the VSCode installer. Install it for user profile only. Do not install it
for all users.

### Test the VSCode install
From a command prompt, type in the following line. After installing VSCode, you
should get similar output as shown below.

```
>code --version
1.44.2
ff915844119ce9485abfe8aa9076ec76b5300ddd
x64
```

To run VSCode, either type `code` in the command line or start Visual Studio
Code from the start menu.

Return to [Check your installation][4].

## Installing Git
Git is a key component to a source, or version, control management system. Git
allows you to make copies of, or clone, remote repositories hosted on sites
like GitHub, GitLab, and code.usgs.gov. Git must be installed and accessible on
your machine in order for you to clone a repository on code.usgs.gov.

### Download Git
Download the latest version of the installer from the [Git page][3].

### Install Git
Run the installer. If possible, do not install Git for all users. While
installing, select VSCode as your editor.

### Test the Git install
To test the Git install, run the following in the command line. If the install
worked, you will see the version number as the output.

```
>git --version
git version 2.21.0.windows.1
```

Return to [Check your installation][4].

[1]: https://www.python.org/downloads/
[2]: https://code.visualstudio.com/download
[3]: https://git-scm.com/
[4]: setup.md#check-your-installation
