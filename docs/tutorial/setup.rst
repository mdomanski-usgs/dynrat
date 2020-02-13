======================================
Setting up the development environment
======================================

Clone the repository
====================
.. code-block:: none

    git clone git@code.usgs.gov:dynamic-rating/dynrat.git

Install the required packages
=============================
.. code-block:: none

    pip install -r requirements.txt

Install the IPython kernel
==========================
.. code-block:: none

    python -m ipykernel install --user --name dynratenv --display-name "Python (dynrat)"

See more at `Installing the IPython kernel <https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments>`_

Install the dynrat package
==========================

In order for the Python interpreter in the dynrat environment to have "global"
access to the dynrat package, you'll have to install the package within the
dynrat environment.

.. code-block:: none

    pip install -e .

Build the documentation (optional)
==================================

.. code-block:: none

    python setup.py build_sphinx
