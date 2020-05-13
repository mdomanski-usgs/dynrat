# DOI SSL Intercept

This tutorial will walk you through adding an SSL intercept root certificate to
your pip configuration. You may need to set up a root certificate if you get
an `SSLError` and on the DOI network when you run pip.

After setting up the DOI SSL intercept root certificate for pip, you must be on
the DOI network to run pip.

## Download the DOI SSL intercept root certificate
Follow [these instructions][1] to download the SSL intercept certificate. Note
the directory you placed the certificate in.

## Configure the pip SSL certificate
Find or create your pip.ini file. The file is located in `%AppData%\pip`. You
can type `%AppData%` into the Windows Explorer address bar to navigate to the
appropriate directory. If the pip directory doesn't exist in the directory,
create it and navigate into it. If pip.ini doesn't exist, create it as a new
text file.

Add the following lines to your pip.ini file, where `<pathToYourCertFile>` is
the path to the SSL certificate file you downloaded in the previous step.

```
[global]
cert=<pathToYourCertFile>
```

Return to
[Install the required packages](setup.md#install-the-required-packages).

[1]: https://github.com/usgs/best-practices/blob/master/ssl/WorkingWithinSSLIntercept.md#0-get-the-ssl-intercept-root-certificate
