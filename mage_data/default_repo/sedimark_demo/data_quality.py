"""Handle duplicate data"""


from data_model import DataSource
from default_repo.sedimark_demo.processing_model import ProcessingStep, ProcessingPipeline




class Dedupe(ProcessingStep) :
    """Implements the algorithms for the deduplication of data"""
    def __init__(self, configuration):
        pass

    def run(self, datasource : DataSource) -> bool :
        ...

    def __train(self, data:DataSource):
        pass

    def __find_duplicates(self, data:DataSource):
        pass

 
class Augment(ProcessingStep):
    ...

class FindMissing(ProcessingStep):
    ...

class FindOutliers(ProcessingStep):
    ...

class Cleaning(ProcessingStep):
    ...

class DQPipeline(ProcessingPipeline) :
    ...


