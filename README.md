# ausdex

![pipline](https://github.com/rbturnbull/ausdex/actions/workflows/pipeline.yml/badge.svg)
[<img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/49262550cc8b0fb671d46df58de213d4/raw/coverage-badge.json">](<https://rbturnbull.github.io/ausdex/coverage/>)
[<img src="https://github.com/rbturnbull/ausdex/actions/workflows/docs.yml/badge.svg">](<https://rbturnbull.github.io/ausdex/>)
[<img src="https://img.shields.io/badge/code%20style-black-000000.svg">](<https://github.com/psf/black>)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
[![status](https://joss.theoj.org/papers/817baa72d2b17b535af8f421a43404b0/status.svg)](https://joss.theoj.org/papers/817baa72d2b17b535af8f421a43404b0)

A Python package for adjusting Australian dollars for inflation.

The Australian Bureau of Statistics (ABS) publishes the Consumer Price Index (CPI) 
for Australia and its capital cities which allows for adjustment of the value of Australian dollars for inflation. 
`ausdex` makes these data available with an inflation calculator in a convenient Python package with simple programmatic and command-line interfaces.

ABS datasets are generally housed in Microsoft Excel spreadsheets linked from the data catalogue. Working with these spreadsheets directly is cumbersome. The `ausdex` package provides an Application Programming Interface (API) for Australian CPI data that seemlessly interoperates with `NumPy` and `pandas`. It makes working with Australian dollars in Python convenient in a similar manner to the [cpi](https://github.com/palewire/cpi) Python package which adjusts US dollars for inflation.

The package is documented here: https://rbturnbull.github.io/ausdex

## Installation

You can install `ausdex` from the Python Package Index (PyPI):

```
pip install ausdex
```

`ausdex` requires Python 3.8 or higher.

To install ausdex for development, see the documentation for [contributing](https://rbturnbull.github.io/ausdex/contributing.html).

## Command Line Usage

Adjust single values using the command line interface:
```
ausdex inflation VALUE ORIGINAL_DATE
```
This adjust the value from the original date to the equivalent for the most recent quarter.

For example, to adjust $26 from July 21, 1991 to the latest quarter run:
```
$ ausdex inflation 26 "July 21 1991" 
$ 52.35
```

To choose a different date for evaluation use the `--evaluation-date` option. This adjusts the value to dollars in the quarter corresponding to that date. For example, this command adjusts $26 from July 1991 to dollars in September 1999:
```
$ ausdex inflation 26 "July 21 1991"  --evaluation-date "Sep 1999"
$ 30.27
```

By default, `ausdex` uses the CPI for Australia in general but you can calculate the inflation for specific capital cities with the `--location` argument:
```
$ ausdex inflation 26 "July 21 1991"  --evaluation-date "Sep 1999" --location sydney
$ 30.59
```

Location options are: 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.


## Module Usage

```
>>> import ausdex
>>> ausdex.calc_inflation(26, "July 21 1991")
52.35254237288135
>>> ausdex.calc_inflation(26, "July 21 1991", evaluation_date="Sep 1999")
30.27457627118644
>>> ausdex.calc_inflation(26, "July 21 1991", evaluation_date="Sep 1999", location="sydney")
30.59083191850594
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

## Dataset and Validation

The Consumer Price Index dataset is taken from the [Australian Bureau of Statistics](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia). It uses the nation-wide CPI value. The validation examples in the tests are taken from the [Australian Reserve Bank's inflation calculator](https://www.rba.gov.au/calculator/). This will automatically update each quarter as the new datasets are released.

The CPI data goes back to 1948. Using dates before this will result in a NaN.

To access the raw CPI data as a pandas DataFrame, use this function:
```
df = ausdex.latest_cpi_df()
```

The Excel spreadsheet for this is stored in the user's cache directory. 
If you wish to download this Excel file to a specific location, use this function:
```
ausdex.files.cached_download_cpi(local_path="cpi-data.xlsx")
```

For more infomation about the methods to download data from the ABS, see the [API specification](https://rbturnbull.github.io/ausdex/reference.html).

## Contributing

See the guidelines for contributing and our code of conduct in the [documentation](https://rbturnbull.github.io/ausdex/contributing.html).

## License and Disclaimer

`ausdex` is released under the Apache 2.0 license.

While every effort has been made by the authors of this package to ensure that the data and calculations used to produce the results are accurate, as is stated in the license, we accept no liability or responsibility for the accuracy or completeness of the calculations. 
We recommend that users exercise their own care and judgment with respect to the use of this package.
 
## Credits

`ausdex` was written by [Dr Robert Turnbull](https://findanexpert.unimelb.edu.au/profile/877006-robert-turnbull) and [Dr Jonathan Garber](https://findanexpert.unimelb.edu.au/profile/787135-jonathan-garber) from the [Melbourne Data Analytics Platform](https://mdap.unimelb.edu.au/).

Please cite from the article when it is released. Details to come soon.

## Acknowledgements

This project came about through a research collaboration with [Dr Vidal Paton-Cole](https://findanexpert.unimelb.edu.au/profile/234417-vidal-paton-cole) and [Prof Robert Crawford](https://findanexpert.unimelb.edu.au/profile/174016-robert-crawford). We acknowledge the support of our colleagues at the Melbourne Data Analytics Platform: [Dr Aleksandra Michalewicz](https://findanexpert.unimelb.edu.au/profile/27349-aleks-michalewicz) and [Dr Emily Fitzgerald](https://findanexpert.unimelb.edu.au/profile/196181-emily-fitzgerald).
