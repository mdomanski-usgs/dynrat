# Setting up GitLab SSH
In order to work with remote repositories hosted on code.usgs.gov through SSH,
you'll need to set up SSH. You do this by creating an SSH key, then adding the
public key to your code.usgs.gov account.

First, start Git Bash (available after installing Git for Windows).

For more detailed information, see
[GitLab and SSH keys](https://code.usgs.gov/help/ssh/README.md).

## Check for existing SSH keys
Type `ls -al ~/.ssh` into the terminal. If you already have existing SSH
public key, they may be named `id_rsa.pub` or something similar. If the command
lists a public key, then you may already have an SSH key on your machine.

## Generate a new SSH key
Type the following command in the terminal, replacing `your_email@usgs.gov`
with your USGS email address.

```
$ ssh-keygen -t rsa -b 4096 -C "your_email@usgs.gov"
```

This creates a new SSH key, using your USGS email as a label.

When prompted for a file name, press Enter. This will save the key in the
default location.

When prompted for a passphrase, you may hit Enter for no passphrase. You will
be prompted to repeat the passphrase. If you did not associate a passphrase
with the SSH key, hit Enter again.

## Add the SSH key to the ssh-agent
In the terminal, type the following command to make sure the ssh-agent is
running.

```
$ eval $(ssh-agent -s)
```

Add the SSH private key to ssh-agent by typing the following command into the
terminal.

```
$ ssh-add ~/.ssh/id_rsa
```

## Add the key to code.usgs.gov
Log in to your USGS GitLab account at [code.usgs.gov](https://code.usgs.gov).

In the upper-right corner of any page, click on your profile photo, then click
**Settings**.

In the user settings sidebar, click **SSH keys**.

Type the following command into the terminal to copy your public SSH key to
your clipboard.

```
$ clip < ~/.ssh/id_rsa.pub
```

Paste the copied SSH key into the **Key** text box.

Add a title for the key in the **Title** text box. The title will typically be
your machine name or *Work Laptop*, etc.

Click the **Add Key** button.

Verify SSH is working by typing the following command into Git Bash.

```
$ ssh -T git@code.usgs.gov
```

Return to [Setting up the development environment](setup.md).
