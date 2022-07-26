from enum import Enum


class Location(str, Enum):
    AUSTRALIA = "Australia"
    SYDNEY = "Sydney"
    MELBOURNE = "Melbourne"
    BRISBANE = "Brisbane"
    ADELAIDE = "Adelaide"
    PERTH = "Perth"
    HOBART = "Hobart"
    DARWIN = "Darwin"
    CANBERRA = "Canberra"

    def __str__(self):
        return self.value
