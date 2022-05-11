---
title: 'ausdex: A Python package for using Australian economic indexing data'
tags:
  - Python
  - economics
  - inflation
authors:
  - name: Robert Turnbull^[co-first author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0003-1274-6750
    affiliation: 1
  - name: Jonathan Garber^[co-first author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0001-6754-4748
    affiliation: 1
affiliations:
 - name: Melbourne Data Analytics Platform, University of Melbourne
   index: 1
date: 10 May 2021
bibliography: paper.bib

---

# Summary

The Australian Bureau of Statistics (ABS) publishes a variety of indexes for the Australian
economic environment. These include the Consumer Price Index (CPI) used for calculating inflation
and various indexes designed to measure socio-economic advantage. `ausdex` makes these data
available in a convenient Python package with a simple programatic and command-line interfaces. 


# Statement of need

`ausdex` is a Python package for querying data produced by the ABS and returning them in a convenient format. Currently ABS data is typically housed in Microsoft Excel spreadsheets linked from the data catalogue. This package interfaces with a subset of the the data to provide an Application Programming Interface (API) to derived economic metrics. For example, we expose the Australian consumer price index data to create an inflation calculator similar to the [cpi](https://github.com/palewire/cpi) Python package for adjusting US dollars.


# Inflation

![Figure 1](docs/images/cpi-time.pdf)
<p align = "center"> Figure 1: The CPI in Australia since 1948.</p>

The Consumer Price Index (CPI) is a weighted average price of a basket of goods and services for urban consumers [@ABS_CPI_Methods]. The ABS issues the Australian CPI [each quarter](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia). The data are available from September 1948 onwards (see fig. 1). The CPI values before decimalization of the Australian currency on February 14, 1966 are in understood according to the conversion rates specified in the 1965 Year Book of Australia such that £1 is equivalent to $2 [@yearbook1965, p. 810].

To adjust prices for inflation, we assume that the ratio of prices for two dates is equal to ratio of the CPIs for those dates [@parkin_macroeconomics_2019, p. 811]. This gives the formula:

$$ \textrm{Price at time B} = \textrm{Price at time A} \times \frac{\textrm{CPI at time B}}{\textrm{CPI at time A}} $$

The `ausdex` package automates the process for downloading the latest version of the Australian CPI data from the ABS. The user enters a price, the original date ($A$) and the evaluation date ($B$) and it returns the adjusted price. The inputs can be scalar values or vectors as a `NumPy` array [@harris2020array], a `pandas` series [@mckinney-proc-scipy-2010] or a `Modin pandas` series [@Petersohn2020]. The size of the returned vector of prices is the same as the vector of original prices. If the original date or the evaluation dates are vectors instead of scalar values then these must be the same size as the vector of prices.

The CPI data for specific capital cities is also reported by the ABS (fig. 2). By default, the CPI for Australia in general is used but specific capital cities can be used for calculating inflation by specifying the location as an argument.

![Figure 2](docs/images/cpi-time-2010.pdf)
<p align = "center"> Figure 2: The CPI in Australian capital cities since 2010.</p>

# Module Features
The components of the module work both from a simple command-line interface and through the API. The code style adheres to PEP 8 [@pep8] through the use of the [Black](https://black.readthedocs.io/en/stable/) Python code formatter. Several scenarios for validation are in the automated tests and these have been compared with the Reserve Bank of Australia's [inflation calculator](https://www.rba.gov.au/calculator/). The automated tests run as part of the CI/CD pipeline and testing coverage is 100%. The package is thoroughly documented at [https://rbturnbull.github.io/ausdex/](https://rbturnbull.github.io/ausdex/).

# Acknowledgements

This project came about through a research collaboration with Vidal Paton-Cole and Robert Crawford (University of Melbourne). We acknowledge the support of our colleagues Aleksandra Michalewicz and Emily Fitzgerald.

# References


