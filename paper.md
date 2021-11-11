---
title: 'ausdex: A Python package for using Australian economic indexing data'
tags:
  - Python
  - economics
  - inflation
  - socio-economic advantage
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
date: 4 October 2021
bibliography: paper.bib

---

# Summary

The Australian Bureau of Statistics (ABS) publishes a variety of indexes for the Australian
economic environment. These include the Consumer Price Index (CPI) used for calculating inflation
and a variety of indexes designed to measure socio-economic advantage. `ausdex` makes these data
available in a convenient Python package with a simple programatic and command line interfaces. 


# Statement of need

`ausdex` is a Python package for querying data produced by the Australian Bureau of Statistics (ABS) and returning them in a convenient format.


# Socio-Economic Indices aggregated from census data for Victoria

Since the 1986 census, the Australian Bureau of statistics (ABS) has generated "Socio Economic Indices For Areas" (SEIFA) following each census. These indices are aggregations of socio economic inputs from the census forms (ie household income, rental/mortgage price, educational level) at teh "census district level" or "mesh level" (2006–current). census districts, or mesh levels, geographic areas statistically defined from the census data to be the largest scale (smallest) geographic building blocks of demographic and socioeconomic data based on population distribution. The Australian Bureau of statistics does aggregate these to other statistical "levels" of geographic area as well as suburbs and local government areas in their "Data Cube" outputs.

However, there have been several new suburbs created during the duration of the SEIFA program. To address this, we used the current suburb areal polygons as the constant spatial areas over which we aggregate previous census datasets. For the 2011 and 2016 SEIFA datasets, we used suburb aggregated data provided by the ABS.

## Spatially aggregating the 1986–2006 datasets

For the SEIFA datasets from 1986 to 2006, we collected census district polygons from aurin (1986–2001) and the ABS data repository (2006), along with associated aggregated SIEFA scores. These census district level SEIFA scores were aggregated to the current suburb GIS datasets using the following steps:

1. Suburbs and census districts were both reprojected to [EPSG:4326](https://spatialreference.org/ref/epsg/wgs-84/)
2. The polygons were unioned together, so the resulting polygon layer had an individual polygon for each overlapping census district and suburb (Figure 1)

3. The merged polygons were reprojected to a utm projected coordinate system [EPSG:32756](https://epsg.io/32756). Note that this utm coordinate system does not overlay the state of victoria perfectly, but we are assuming that locally the measured areas are relatively accurate to each other.

4. The SEIFA scores were aggregated for all of the census district parts within each suburb using a weighted average, with the polygon area as the weight.

![Figure 1](paper_images/example_overlay.png)
<p align = "center"> Figure 1: map of three suburb outlines (black lines) for Richmond (left), Burnley (center), and Hawthorne (right) overlaying 1986 Census Districts (colored polygons with white boundaries). The census districts are colored according to the census district code. Note that these districts do not line up with subur boundaries. the green district in the lower middle section falls in parts of Richmond, and cremorne. Likewise one of the Orange and Purple Census districts spans two suburbs.</p>

# Inflation

The ABS issues [updates](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia) to the Australian Consumer Price Index (CPI) every quarter. 

[Australian Bureau of Statistics]

The Consumer Price Index dataset is taken from the . It uses the nation-wide CPI value. The validation examples in the tests are taken from the [Australian Reserve Bank's inflation calculator](https://www.rba.gov.au/calculator/). This will automatically update each quarter as the new datasets are released.

The CPI data goes back to 1948. Using dates before this will result in a NaN.

# Module Features
The module is thoroughly documented at [https://rbturnbull.github.io/ausdex/](https://rbturnbull.github.io/ausdex/). 
Testing coverage


# Acknowledgements

This project came about through a research collaboration with Vidal Paton-Cole and Robert Crawford. We acknowledge the support of our colleagues at the Melbourne Data Analytics Platform, Aleksandra Michalewicz and Emily Fitzgerald.

# References
