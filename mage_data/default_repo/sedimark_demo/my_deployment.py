from processing_model import Orchestrator
from data_model import DataStore_NGSILD
import data_quality
import connector 


orchestrator = None
data_store = None
pipeline1 = None


# This file demonstrates how the Sedimark toolbox could be
# integrated in a given dataspace.


# Run at the initialization of the Sedimark Toolbox
def init():
    global data_store,orchestrator

    data_store = connector.DataStore_NGSILD("host","login","passw")

    # Setup the data quality pipeline
    # This should probably be more dynamic than what is presented here

    orchestrator = Orchestrator()
    orchestrator.register_step(data_quality.Dedupe)
    orchestrator.register_step(data_quality.Augment)
    orchestrator.register_step(data_quality.FindMissing)
    orchestrator.register_step(data_quality.FindOutliers)
    orchestrator.register_step(data_quality.Cleaning)

    orchestrator.register_step(connector.SaveData_NGSILD)
    orchestrator.register_step(connector.LoadData_NGSILD)

    # Remark : this is a quite generic processing framework, could 
    # integrate a lot more than only data quality (T3.4)
    

# Run at some point by the user interface (Web based or Python scripts or ...)
def setup_pipeline1():
    pipeline2 = orchestrator.build_pipeline(
        dag_script= {
            # Here is the DAG script (using a dict as a generic format for quick prototyping)
            # DCAT / ONNX format here ?
            
            "LoadData_NGSILD" : {"name":"S1", "urn":"urn:ngsi-ld:the:input:abc1"}, 
            # we could have here some mapping instructions between let's say, NGSI-LD and the internal format
            
            "LoadData_NGSILD" : {"name":"S2", "urn":"urn:ngsi-ld:the:input:abc2"},
            
            "Dedupe" : {"name":"DS1", "source":"S1", "param1":12, "param2":3.72, "depends" : ["S1"]},
            # The parameters of this step may provide on which "columns" to act (for example), this is linked to
            # the mapping provided at the previous step

            "SaveData_NGSILD" : {"name":"SaveDS1", "source":"res", "target":"urn:ngsi-ld:the:output:abc1:deduped", "depends" : ["DS1"]},
            
            "Dedupe" : {"name":"DS2", "source":"S2", "param1":12, "param2":3.72, "depends" : ["S2"]},
            "Cleaning" : {"name":"CS2", "source":"DS2", "paramA":94, "param2":"A,C,T", "depends" : ["DS2"]},
            "Diff" : {"name":"res", "left":"DS1", "right":"CS2", "depends" : ["DS1","CS2"]},
            "SaveData_NGSILD" : {"source":"res", "target":"urn:ngsi-ld:the:output:abc:diff"}
    }
    
            # Many types of "processing" steps can be thought up, even not real "processings"
            # like PublishToOffering, ...
    )

    # Here we should probably persist this pipeline somewhere
    # + provide a triggering condition.
    data_store.subscribe("urn:ngsi-ld:the:input:abc1", trigger_pipeline1) # Something like this ?



# Run when the triggering condition is met
def trigger_pipeline1():
    orchestrator.run_pipeline(pipeline1)
    

