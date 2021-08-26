# aucpi

Adjusts Australian dollars for inflation.

## Installation

You can install the development version directly from github:

```
pip install git+https://github.com/rbturnbull/aucpi.git
```

## Command Line Usage

Adjust single values using the command line interface:
```
aucpi VALUE ORIGINAL_DATE
```
This adjust the value from the original date to the equivalent in today's dollars.

For example, to adjust $26 from July 21, 1991 to today run:
```
$ aucpi 26 "July 21 1991" 
$ 52.35
```

To choose a different date for evaluation use the `--evaluation-date` option. e.g.
```
$ aucpi 26 "July 21 1991"  --evaluation-date "Sep 1999"
$ 30.27
```

## Module Usage

```
>>> import aucpi
>>> aucpi.adjust(26, "July 21 1991")
52.35254237288135
>>> aucpi.adjust(26, "July 21 1991",evaluation_date="Sep 1999")
30.27457627118644
```
The dates can be as strings or Python datetime objects.

The values, the dates and the evaluation dates can be vectors by using NumPy arrays or Pandas Series. e.g.
```
>>> df = pd.DataFrame(data=[ [26, "July 21 1991"],[25,"Oct 1989"]], columns=["value","date"] )
>>> df['adjusted'] = aucpi.adjust(df.value, df.date)
>>> df
   value          date   adjusted
0     26  July 21 1991  52.352542
1     25      Oct 1989  54.797048
```

## Dataset and Validation
The Consumer Price Index dataset is taken from the Australian Bureau of Statistics (https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia). It uses the nation-wide CPI value. The validation examples in the tests are taken from the Australian Reserve Bank's inflation calculator (https://www.rba.gov.au/calculator/).

The CPI data goes back to 1948. Using dates before this will result in a NaN.

NB. The code is currently hardcoded to download the CPI data for June 2021. This means that future dates will use CPI values from this this date. This will be fixed in a future update.

## Development

To devlop aucpi, clone the repo and install the dependencies using poetry:

```
git clone https://github.com/rbturnbull/aucpi.git
cd aucpi
poetry install
```

You can enter the environment by running:

```
poetry shell
```

The tests can be run using `pytest`.

## Credits

Robert Turnbull (University of Melbourne)
