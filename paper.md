---
title: 'ausdex: A Python package for adjusting Australian dollars for inflation'
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

The Australian Bureau of Statistics (ABS) publishes the Consumer Price Index (CPI) 
for Australia and its capital cities, which allows for adjustment of the value of Australian dollars for inflation. 
`ausdex` makes these data available with an inflation calculator
in a convenient Python package with simple programmatic and command-line interfaces.

# Statement of need

Understanding price inflation is critical to any economic analysis and is one of the key economic concerns in a post-pandemic global economy [@hung2021output]. It is important to be able to quickly incorporate measures of inflation and correct historic prices to current values in order to reflect the real change in purchasing power and the value of goods. To that end, we have built a package to automate the collection and calculation of inflation data for Australia, as well as for major Australian cities, using data supplied by the ABS.

ABS datasets are generally housed in Microsoft Excel spreadsheets linked from the data catalogue. Working with these spreadsheets directly is cumbersome. The `ausdex` package provides an Application Programming Interface (API) for Australian CPI data that seemlessly interoperates with `NumPy` [@harris2020array] and `pandas` [@mckinney-proc-scipy-2010]. It makes working with Australian dollars in Python convenient in a similar manner to the [cpi](https://github.com/palewire/cpi) Python package which adjusts US dollars for inflation.

This software project was developed for the purpose of performing an analysis of a time series of building permits in Victoria, Australia. Corrections due to inflation were needed in order to compare the costs of renovations and new building project along a multi-decadal timespan. The results of these studies were presented at the 2022 CIB World Building Conference [@crawford_trends_2022; @paton-cole_trends_2022]. This software would be of use for any analysis of Australian prices over a period of time for which inflationary effects need to be accounted.

# Calculating Inflation

The Consumer Price Index (CPI) is a weighted average price of a basket of goods and services for urban consumers [@ABS_CPI_Methods]. The ABS issues the Australian CPI [each quarter](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia). The data are available from September 1948 onwards (see Figure 1). The CPI values before decimalization of the Australian currency on February 14, 1966 are understood according to the conversion rates specified in the 1965 Year Book of Australia such that £1 is equivalent to $2 [@yearbook1965, p. 810].

![The CPI in Australia since 1948](docs/images/cpi-time.pdf)

To adjust prices for inflation, we assume that the ratio of prices for two dates is equal to the ratio of the CPIs for those dates [@parkin_macroeconomics_2019, p. 811]. This gives the formula:

$$ \textrm{Price at time B} = \textrm{Price at time A} \times \frac{\textrm{CPI at time B}}{\textrm{CPI at time A}} $$

# Package Description

The `ausdex` package automates the process for downloading the latest version of the Australian CPI data from the ABS. The user enters a price, the original date ($A$) and the evaluation date ($B$) and it returns the adjusted price. The inputs can be scalar values or vectors as a `NumPy` array, a `pandas` series or a `Modin pandas` series [@Petersohn2020]. The size of the returned vector of prices is the same as the vector of original prices. If the original date or the evaluation dates are vectors instead of scalar values, then these must be the same size as the vector of prices.

The CPI data for specific capital cities is also reported by the ABS (Figure 2). By default, the CPI for Australia as a whole is used but specific capital cities can be used for calculating inflation by specifying the location as an argument.

![The CPI in Australian capital cities since 2012](docs/images/cpi-time-2012.pdf)

The components of the module work both from a simple command-line interface and through the API. The code style adheres to PEP 8 [@pep8] through the use of the [Black](https://black.readthedocs.io/en/stable/) Python code formatter. Several scenarios for validation are in the automated tests and these have been compared with the Reserve Bank of Australia's [inflation calculator](https://www.rba.gov.au/calculator/). The automated tests run as part of the continuous integration pipeline and testing coverage is 100%. The package is thoroughly documented at [https://rbturnbull.github.io/ausdex/](https://rbturnbull.github.io/ausdex/).

# Acknowledgements

This project came about through a research collaboration with Vidal Paton-Cole and Robert Crawford (Melbourne School of Design, University of Melbourne). We acknowledge the support of our colleagues Aleksandra Michalewicz and Emily Fitzgerald at the Melbourne Data Analytics Platform.

# References


