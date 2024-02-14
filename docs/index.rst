.. ausdex documentation master file, created by
   sphinx-quickstart on Mon Oct  4 11:44:45 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


ausdex
======================================================================


Welcome to the documentation for ``ausdex``, a Python package for adjusting Australian dollars for inflation.

The Australian Bureau of Statistics (ABS) publishes the Consumer Price Index (CPI) 
for Australia and its capital cities which allows for adjustment of the value of Australian dollars for inflation. 
``ausdex`` makes these data available with an inflation calculator in a convenient Python package with simple programmatic and command-line interfaces.

ABS datasets are generally housed in Microsoft Excel spreadsheets linked from the data catalogue. 
Working with these spreadsheets directly is cumbersome. 
The ``ausdex`` package provides an Application Programming Interface (API) for Australian CPI data that seemlessly interoperates with ``NumPy`` and ``pandas``. 

More information about ``ausdex`` can be found in the paper about the packge in the Journal of Open Source Software: https://doi.org/10.21105/joss.04212

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   reference
   cli
   visualization   
   citation
   contributing
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
