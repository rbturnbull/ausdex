# Quickstart

## Installation

You can install `ausdex` from the Python Package Index (PyPI):

```
pip install ausdex
```

`ausdex` requires Python 3.8 or higher.

To install `ausdex` for development, see the documentation for [contributing](./contributing.md).

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
54.6
>>> ausdex.calc_inflation(26, "July 21 1991", evaluation_date="Sep 1999")
30.27457627118644
>>> ausdex.calc_inflation(26, "July 21 1991", evaluation_date="Sep 1999", location="sydney")
30.59083191850594
```
The dates can be as strings or Python datetime objects.

The values, the dates and the evaluation dates can be vectors by using NumPy arrays or Pandas Series. e.g.
```
>>> df = pd.DataFrame(data=[ [26, "July 21 1991"],[25,"Oct 1989"]], columns=["value","date"] )
>>> df['adjusted'] = ausdex.inflation(df.value, df.date)
>>> df
   value          date   adjusted
0     26  July 21 1991  52.352542
1     25      Oct 1989  54.797048
```

## Dataset and Validation
The Consumer Price Index dataset is taken from the [Australian Bureau of Statistics](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia). It uses the nation-wide CPI value. The validation examples in the tests are taken from the [Australian Reserve Bank's inflation calculator](https://www.rba.gov.au/calculator/). This will automatically update each quarter as the new datasets are released.

The CPI data goes back to 1948. Using dates before this will result in a NaN.

## License and Disclaimer

`ausdex` is released under the Apache 2.0 license.

While every effort has been made by the authors of this package to ensure that the data and calculations used to produce the results are accurate, as is stated in the license, we accept no liability or responsibility for the accuracy or completeness of the calculations. 
We recommend that users exercise their own care and judgment with respect to the use of this package.
