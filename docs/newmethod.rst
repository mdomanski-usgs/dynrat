=============
New Algorithm
=============

Mass
----

.. math:: \frac{\partial A}{\partial t} + \frac{\partial Q}{\partial x} = 0
    :label: NewAlgo.1

Momentum
--------

.. math:: \frac{\partial Q}{\partial t}
    + \frac{\partial\left(\beta QV\right)}{\partial x}
    + gA\left(\frac{\partial h}{\partial x} + S_f\right) = 0
    :label: NewAlgo.2

Where

.. math:: \frac{\partial h}{\partial x} = \frac{\partial y}{\partial x} - S_o
    :label: NewAlgo.3

.. math:: \beta = \frac{A}{K^2}\sum_i^N\frac{K_i^2}{A_i}
    :label: NewAlgo.4

.. math:: K_i = \frac{1.486}{n_i}A_iR_i^{2/3}
    :label: NewAlgo.5

.. math:: Q = KS_f^{1/2}
    :label: NewAlgo.6

Substituting :eq:`NewAlgo.3` into :eq:`NewAlgo.2` and carrying out the
multiplication of :math:`gA`

.. math:: \frac{\partial Q}{\partial t}
    + \frac{\partial\left(\beta QV\right)}{\partial x}
    + gA\frac{\partial y}{\partial x} + gAS_f - gAS_o = 0
    :label: NewAlgo.7

Expanding the second term in :eq:`NewAlgo.7` and using :math:`V=Q/A`

.. math:: \frac{\partial\left(\beta QV\right)}{\partial x} =
    \frac{\partial\left(\beta Q^2/A\right)}{\partial x}
    =  Q^2/A\frac{\partial\beta}{\partial x}
    + \beta\frac{\partial\left(Q^2/A\right)}{\partial x}

Assuming :math:`Q^2/A\frac{\partial\beta}{\partial x} \ll \beta\frac{\partial\left(Q^2/A\right)}{\partial x}`

.. math:: \beta\frac{\partial\left(Q^2/A\right)}{\partial x}
    = \beta\left(\frac{2Q}{A}\frac{\partial Q}{\partial x}
    - \frac{Q^2}{A^2}\frac{\partial A}{\partial x}\right)

To take care of the discharge spatial derivative, rearrange :eq:`NewAlgo.1`.

.. math:: \frac{\partial Q}{\partial x} = -\frac{\partial A}{\partial t}

The area spatial derivative becomes

.. math:: \frac{\partial A}{\partial x} =
    \frac{\partial A}{\partial y}\frac{\partial y}{\partial x} =
    B\frac{\partial y}{\partial x}

Finally, the second term in :eq:`NewAlgo.7` becomes :eq:`NewAlgo.8`.

.. math:: \frac{\partial\left(\beta QV\right)}{\partial x} =
    -\beta\frac{2Q}{A}\frac{\partial A}{\partial t}
    -\beta B\frac{Q^2}{A^2}\frac{\partial y}{\partial x}
    :label: NewAlgo.8

Substituting :eq:`NewAlgo.8` into :eq:`NewAlgo.7` and dividing through by
:math:`gA` gives :eq:`NewAlgo.9`

.. .. math:: \frac{1}{gA}\frac{\partial Q}{\partial t}
    - \beta\frac{2Q}{gA^2}\frac{\partial A}{\partial t}
    - \beta B\frac{Q^2}{gA^3}\frac{\partial y}{\partial x}
    + \frac{\partial y}{\partial x} + S_f - S_o = 0

.. math:: \frac{1}{gA}\frac{\partial Q}{\partial t}
    - \beta\frac{2Q}{gA^2}\frac{\partial A}{\partial t}
    + \left(1 - \beta B\frac{Q^2}{gA^3}\right)\frac{\partial y}{\partial x}
    + S_f - S_o = 0
    :label: NewAlgo.9

Under the kinematic wave assumption

.. math:: \frac{\partial y}{\partial x} =
    -\frac{1}{c}\frac{\partial h}{\partial t} - \frac{2S_o}{3r^2}

.. math:: c = \frac{1}{B}\frac{dQ}{dh}

:math:`Q = KS_o^{1/2}`

.. math:: c = \frac{S_o^{1/2}}{B}\frac{dK}{dh}

This makes :math:`\frac{\partial y}{\partial x}` a function of :math:`h` only.

Since :math:`Q = KS_f^{1/2}` and :math:`K` is a function of :math:`h`, :math:`Q`
is a function of :math:`h` and :math:`S_f`.
