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

`ausdex` is a Python package for querying data produced by the Australian Bureau of Statistics (ABS) and returning them in a convenient format. Currently ABS data is housed typically in excel spreadsheets linked from the data catalogue. This package attempts to interface with a subset of the the data in order to provide an api to derived socio economic metrics. One metric we expose is to use ABS consumer price index data to create an inflation calculator similar to  the [python cpi package](https://github.com/palewire/cpi) in the United States. 

In addition, we bring api access to ABS Socioeconomic index data for areas (SEIFA) aggregated at the suburb level in Victoria. This allows for quick assessment of the socioeconomic history of a suburb in Victoria from historic census data. The ABS calculates these variables every 5 years (on the 1st and 6th year of a decade) and has been calculating SEIFA metrics since 1986. These datasets are housed in different online repositories, and are aggregated to different spatial extents, due to the fact that statistical geographic boundaries are redrawn from every census dataset. The `ausdex.seifa_vic` submodule allows for the circumventing of downloading and combining datasets from different data sources, and allows for time series comparisons tied to the current suburb geographic boundaries. 

# Socio-Economic Indices aggregated from census data for Victoria

Since the 1986 census, the Australian Bureau of statistics (ABS) has generated "Socio Economic Indices For Areas" (SEIFA) following each census. Information on the calculation of these indices can be found here 
[@abs_2016_seifa_tp; @abs_2011_seifa_tp; @abs_2001_seifa_tp]

<!-- @abs_2006_seifa_tp; @abs_2001_seifa_tp; @abs_1996_seifa_tp] -->

These indices are aggregations of socio economic inputs from the census forms (ie household income, rental/mortgage price, educational level) at the "census district level" or "mesh level" (2006–current). census districts, or mesh levels, geographic areas statistically defined from the census data to be the largest scale (smallest) geographic building blocks of demographic and socioeconomic data based on population distribution. These statistical geographies are redrawn after every census. The Australian Bureau of statistics does aggregate these to other statistical "levels" of geographic area from the Australian Statistical Geography Standard (ASGS) ([Statistical Areas levels 1 - 4](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026)) [@abs_2016_sa1_shape] suburbs and local government areas in their "Data Cube" outputs. 

However, there have been several new suburbs created during the duration of the SEIFA program, and suburb aggregated datasets are not readily available for Census data before 2006.  To address this, we used the current Victorian suburb areal polygons [@vic_suburbs] as the constant spatial areas over which we aggregate all previous census datasets. In order to overcome suburb names that are repeated. The suburb polygons were also overlain with local government areas[@vic_lga] to make duplicate suburbs distinct.

## Spatially aggregating the 1986–2006 datasets

For the SEIFA datasets from 1986 to 2006, we collected census district polygons from aurin [@aurin_portal] and the ABS data repository (2006), along with associated aggregated SIEFA scores. These census district level SEIFA scores were aggregated to the current suburb GIS datasets [@vic_suburbs] using the following steps:

1. Suburbs and census districts were both reprojected to [EPSG:4326](https://spatialreference.org/ref/epsg/wgs-84/)
2. The polygons were unioned together, so the resulting polygon layer had an individual polygon for each overlapping census district and suburb (Figure 1)

3. The merged polygons were reprojected to a utm projected coordinate system [EPSG:32756](https://epsg.io/32756). Note that this utm coordinate system does not overlay the state of victoria perfectly, but we are assuming that locally the measured areas are relatively accurate to each other.

4. The SEIFA scores were aggregated for all of the census district parts within each suburb using a weighted average, with the polygon area as the weight.

![Figure 1](paper_images/paper_output.svg)
<p align = "center"> Figure 1: map of three suburb outlines (black lines) for Richmond (left), Burnley (center), and Hawthorne (right) overlaying 1986 Census Districts (colored polygons with white boundaries). The census districts are colored according to the census district code. Note that these districts do not line up with subur boundaries. the green district in the lower middle section falls in parts of Richmond, and cremorne. Likewise one of the Orange and Purple Census districts spans two suburbs.</p>

## Spatially aggregating the 2011 and 2016 datasets

For the 2011 and 2016 datasets, we used the same outline above, but started with a different statistical geographic dataset.  We used statistical srea one (SA1) aggregated estimates of the seifa variables published as an ABS data cube, and GIS polygons of SA1 boundaries from the ASGS created for 2011 and 2016 to derive suburb aggregated datasets.

## List of data sources for seifa vic submodule

| year | dataset type | dataset source |
| :---- | :------------ | :-------------- |
| 1986 | census district polygons and metrics | [@aurin_portal] wfs id: `AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1986`| 
| 1991 | census district polygons and metrics | [@aurin_portal] wfs id: `AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1991`|
| 1996 | census district polygons and metrics | [@aurin_portal] wfs id: `AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1996`|
| 2001 | census district polygons and metrics | [@aurin_portal] wfs id: `AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_2001`|
| 2006 | ABS census district shapefile| [@abs_2006_cd_shape] [download link](https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1259030002_cd06avic_shape.zip&1259.0.30.002&Data%20Cubes&D62E845F621FE8ACCA25795D002439BB&0&2006&06.12.2011&Previous)|
| 2006 | ABS census district seifa metrics | [@abs_2006_seifa]  [download link](https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033055001_%20seifa,%20census%20collection%20districts,%20data%20cube%20only,%202006.xls&2033.0.55.001&Data%20Cubes&6EFDD4FA99C28C4ECA2574170011668A&0&2006&26.03.2008&Latest)|
| 2011 | ABS SA1 Polygons | [@abs_2011_sa1_shape] [download link](https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&1270055001_sa1_2011_aust_shape.zip&1270.0.55.001&Data%20Cubes&24A18E7B88E716BDCA257801000D0AF1&0&July%202011&23.12.2010&Latest)|
| 2011 | ABS SA1 seifa metrics | [@abs_2011_seifa] [download link](https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033.0.55.001%20sa1%20indexes.xls&2033.0.55.001&Data%20Cubes&9828E2819C30D96DCA257B43000E923E&0&2011&05.04.2013&Latest)|
| 2016 | ABS SA1 Polygons | [@abs_2016_sa1_shape]  [download link](https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1270055001_sa1_2016_aust_shape.zip&1270.0.55.001&Data%20Cubes&6F308688D810CEF3CA257FED0013C62D&0&July%202016&12.07.2016&Latest)|
| 2016 | ABS SA1 seifa metrics | [@abs_2016_seifa] [download link](https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&2033055001%20-%20sa1%20indexes.xls&2033.0.55.001&Data%20Cubes&40A0EFDE970A1511CA25825D000F8E8D&0&2016&27.03.2018&Latest)|
| all | VicMap suburb polygons| [@vic_suburbs] [download link](https://data.gov.au/geoserver/vic-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_af33dd8c_0534_4e18_9245_fc64440f742e&outputFormat=json)|
| all | VicMap Local Government Area Polygons| [@vic_lga]  [download link](https://data.gov.au/geoserver/vic-local-government-areas-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_bdf92691_c6fe_42b9_a0e2_a4cd716fa811&outputFormat=json)|
 



# Inflation

The ABS issues [updates](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia) to the Australian Consumer Price Index (CPI) every quarter. 

[Australian Bureau of Statistics]

The Consumer Price Index dataset is taken from the . It uses the nation-wide CPI value. The validation examples in the tests are taken from the [Australian Reserve Bank's inflation calculator](https://www.rba.gov.au/calculator/). This will automatically update each quarter as the new datasets are released.

The CPI data goes back to 1948. Using dates before this will result in a NaN.

# Module Features
The module is thoroughly documented at [https://rbturnbull.github.io/ausdex/](https://rbturnbull.github.io/ausdex/). 
Testing coverage

black
typer

## Command Line Usage

Adjust single values using the command line interface:
```
ausdex inflation VALUE ORIGINAL_DATE
```
This adjust the value from the original date to the equivalent in today's dollars.

For example, to adjust $26 from July 21, 1991 to today run:
```
$ ausdex inflation 26 "July 21 1991" 
$ 52.35
```

To choose a different date for evaluation use the `--evaluation-date` option. e.g.
```
$ ausdex inflation 26 "July 21 1991"  --evaluation-date "Sep 1999"
$ 30.27
```

### seifa_vic command line usage
you can use the seifa-vic command to interpolate an ABS census derived Socio economic score for a given year, suburb, and SEIFA metric
```
$ ausdex seifa-vic 2020 footscray ier_score
$ 861.68

```

## Module Usage

```
>>> import ausdex
>>> ausdex.calc_inflation(26, "July 21 1991")
52.35254237288135
>>> ausdex.calc_inflation(26, "July 21 1991",evaluation_date="Sep 1999")
30.27457627118644
```
The dates can be as strings or Python datetime objects.

The values, the dates and the evaluation dates can be vectors by using NumPy arrays or Pandas Series. e.g.
```
>>> df = pd.DataFrame(data=[ [26, "July 21 1991"],[25,"Oct 1989"]], columns=["value","date"] )
>>> df['adjusted'] = ausdex.calc_inflation(df.value, df.date)
>>> df
   value          date   adjusted
0     26  July 21 1991  52.352542
1     25      Oct 1989  54.797048
```
### seifa_vic submodule

Like using the `calc_inflation` function, the `interpolate_vic_suburb_seifa` takes in a date argument (integer, str, datetime.datetime, np.datetime64 ) that can be in a series (list, np.array, pd.Series, modin.pandas.Series). Likewise, the suburb input can be a single string, or a series of strings (list, np.array, pd.Series, modin.pandas.Series) associated with each date value in the date input. The name of the SEIFA score is also specified. 

```python
>>> from ausdex.seifa_vic import interpolate_vic_suburb_seifa
>>> interpolate_vic_suburb_seifa(2007, 'FOOTSCRAY', 'ier_score')
874.1489807920245
>>> interpolate_vic_suburb_seifa([2007, 2020], 'FOOTSCRAY', 'ier_score', fill_value='extrapolate')
array([874.14898079, 861.68112674])
```

You can also feed in lists of suburbs, as well as local government areas (lga), to account for suburb names that are used
multiple times in the same state.

```python
>>> interpolate_vic_suburb_seifa(
  np.array(['31-05-2010', '10-03-1988', '10-03-2025']),
  pd.Series(['Ascot', 'Ascot', 'Abbotsford']),
  'ier_score',
  lga = ['ballarat', 'greater bendigo', 'Yarra']
  )
array([1084.16837443, 1052.41809538,           nan])
```

## Notes 
* Cite scipy for interpolation [@jones_scipy:_2001]
* Cite numpy
* Cite pandas [@mckinney-proc-scipy-2010]
* Cite inflation equation source
* Cite similar US library?
* Cite aurin

* Trewin, D. (2001), Census of population and housing: Socio-economic indexes for area’s (SEIFA), Australian Bureau of Statistics
(ABS), Canberra.

* https://aurin.org.au/legal/copyright-and-attribution/
[Data Source Organisation], ([Year]): [Dataset Title]; accessed from [[AURIN Portal]/AURIN Workbench/[name AURIN sub-site]] on [date of access]


# Acknowledgements

This project came about through a research collaboration with Vidal Paton-Cole and Robert Crawford. We acknowledge the support of our colleagues at the Melbourne Data Analytics Platform, Aleksandra Michalewicz and Emily Fitzgerald.

This app uses the NCRIS-enabled Australian Urban Research Infrastructure Network (AURIN) Portal e-Infrastructure to access the following datasets:  AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1986, AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1991, AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1996, and AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_2001.

# References


