from default_repo.sedimark_demo.data_model import DataSource

class ProcessingStep :
    # A ProcessingStep implements a run method
    def __init__(self, config : dict) -> None:
        self.config = config

    def run(self, context : dict ) -> bool:
        ...

class ProcessingPipeline(ProcessingStep) : #I'm still not sure about the ProcessingStep subclassing
    # A ProcessingPipeline is a "DAG script" ProcessingStep

    def __init__(self, configuration : dict) -> None:
        super().__init__()
        self.cfg = configuration
        self.steps = []

    def register_step(self, step: ProcessingStep) :
        self.steps.append(step)


class ProcessingReport :
    def __init__(self,step) -> None:
        self.processing = self.step




class Orchestrator :
    # This is probably the proxy to a known and already implemented orchestrator

    def __init__(self) -> None:
        self.known_steps = {} # k:step type id ; value:ProcessingStep subclass

    # ### STEPS MANAGEMENT

    def register_step(self, step : type[ProcessingStep]) -> None:
        ...
        self.known_steps[step.__name__] = step
        ...

    def instantiate_step(id:str, cfg:dict) -> ProcessingStep :
        ...

    def list_known_steps(self) -> dict :
        return self.known_steps


    # ### PIPELINE MANAGEMENT

    def build_pipeline(self, dag_script : dict) -> ProcessingPipeline:
        pipeline_cfg = {} # whatever is needed to configure the pipeline itself.
        pipeline = ProcessingPipeline(pipeline_cfg)

        # Use here the DAG script to instanciate and configure 
        # the ProcessingSteps objects
        # The format of the DAG script can be anything, like ONNX 
        # (I put a dict as a generic format)
        ...
        step_cfg = {} # whatever is needed to configure the step itself.
        astep = self.instanciate_step("step_type", step_cfg)
        pipeline.register_step(astep)
        ...


    def run_pipeline(self, pipeline: ProcessingPipeline) -> ProcessingReport:
        ...
        context = {}
        for step in pipeline.steps : 
            # very naive loop, missing a lot of functionalities
            # i.e. multiple data sources, processing order wrt DAG, multi-threading, ...
            # the idea is to show how data can be transmitted from one step to another
            step.run(context)


