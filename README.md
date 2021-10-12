# aucpi

![pipline](https://github.com/rbturnbull/aucpi/actions/workflows/coverage.yml/badge.svg)
[<img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/49262550cc8b0fb671d46df58de213d4/raw/coverage-badge.json">](<https://rbturnbull.github.io/aucpi/coverage/>)
[<img src="https://github.com/rbturnbull/aucpi/actions/workflows/docs.yml/badge.svg">](<https://rbturnbull.github.io/aucpi/>)
[<img src="https://img.shields.io/badge/code%20style-black-000000.svg">](<https://github.com/psf/black>)

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

### seifa_vic command line usage
youc an use the seifa-vic command to interpolate an ABS census derived Socio economic score for a given year, suburb, and SEIFA metric
```
$ aucpi seifa-vic 2020 footscray ier_score
$ 861.68

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
### seifa_vic submodule

```python
>>> from aucpi.seifa_vic import interpolate_vic_suburb_seifa
>>> interpolate_vic_suburb_seifa(2007, 'FOOTSCRAY', 'ier_score')
874.1489807920245
>>> interpolate_vic_suburb_seifa([2007, 2020], 'FOOTSCRAY', 'ier_score', fill_value='extrapolate')
array([874.14898079, 861.68112674])
```

## Dataset and Validation
The Consumer Price Index dataset is taken from the Australian Bureau of Statistics (https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia). It uses the nation-wide CPI value. The validation examples in the tests are taken from the Australian Reserve Bank's inflation calculator (https://www.rba.gov.au/calculator/). This will automatically update each quarter as the new datasets are released.

The CPI data goes back to 1948. Using dates before this will result in a NaN.

### seifa_vic datasets
Data for the socio economic scores by suburbs comes from a variety of sources, and goes between 1986 to 2016 for the index of economic resources, and the index of education and opportunity, other indices are only available for a subset of census years

When this module is first used, data will be downloaded and preprocessed from several locations. Access to the aurin API is necessary via this [form](https://aurin.org.au/resources/aurin-apis/sign-up/). You will be prompted to enter the username and password when you first run the submodule. This will be saved in the app user directory for future use. You can also create a config.ini file in the repository folder with the following:

```toml
[aurin]
username = {aurin_api_username}
password = {aurin_api_password}
```

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
