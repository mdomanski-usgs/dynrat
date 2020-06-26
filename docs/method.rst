======
Method
======

Fread's method
==============

Mass
----

.. math:: A\frac{\partial V}{\partial x} + V \frac{\partial A}{\partial x}
    + B\frac{\partial h}{\partial t} = 0

Momentum
--------

.. math:: \frac{\partial V}{\partial t} + V\frac{\partial V}{\partial x}
    + g\left(\frac{\partial y}{\partial x} + S_f - S_o\right) = 0

.. math:: Q = \frac{1.486}{n}AR^{2/3}S^{1/2}

HEC-RAS
=======

Mass
----

.. math:: \frac{\partial A}{\partial t} + \frac{\partial Q}{\partial x} = 0

Momentum
--------

.. math:: \frac{\partial Q}{\partial t}
    + \frac{\partial\left(\beta QV\right)}{\partial x}
    + gA\left(\frac{\partial h}{\partial x} + S_f\right) = 0

.. math:: \frac{\partial h}{\partial x} = \frac{\partial y}{\partial x}
    + \frac{\partial h_0}{\partial x}

.. math:: \beta = \frac{A}{K^2}\sum_i^N\frac{K_i^2}{A_i}

.. math:: K_i = \frac{1.486}{n_i}A_iR_i^{2/3}

.. math:: Q = KS_f^{1/2}
