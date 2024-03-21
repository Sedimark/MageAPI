"""The base classes to handle the data of the Sedimark platform"""

from typing import Callable

class DataSource :
    """The generic class for data sources in SEDIMARK

    - Should basically handle "records" and "fields"
    - Could we simply use here a Pandas dataframe here ? or embed one with additional data ?
    """


class DataSet(DataSource) :
    """Class to connect to a complete dataset"""
    pass



class DataStream(DataSource) :
    """Class to connect to a stream of data"""
    pass



class DataStore :
    def get_data(self, datasource_id) -> DataSource:
        """Return a proxy to a data source"""
        pass

    def subscribe(self, target : str, hook : Callable) -> None :
        ...

