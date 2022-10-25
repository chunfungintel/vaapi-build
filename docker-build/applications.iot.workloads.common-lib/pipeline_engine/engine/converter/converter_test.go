package converter

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"testing"

	"github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/controller"
)

func TestPipeline_Converter_Parse_Pipeline_JSON(t *testing.T) {
	jsonFile, err := os.Open("../test_data/pipelines/4k-videowall-vacomp-4kenc-pipeline.json")
	if err != nil {
		t.Fatalf("Unexpected error opening json file: %v", err)
	}
	defer jsonFile.Close()

	jsonBytes, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		t.Fatalf("Unexpected error reading json file: %v", err)
	}

	var pipeline controller.Pipeline

	if err := json.Unmarshal(jsonBytes, &pipeline); err != nil {
		t.Fatalf("Unexpected error unmarshalling json: %v", err)
	}

	envars := make(map[string]string)
	envars["datasetsDir"] = "/usr/local/data"
	envars["outputDir"] = "/usr/local/output"

	if err := controller.ParsePipeline(&pipeline, envars); err != nil {
		t.Fatalf("Unexpected error parsing json: %v", err)
	}

	dag := PipelineToDAG(&pipeline)
	r := DAGToString(dag)
	t.Logf("parsed DAG:\n%v", r)

	CountPipelines(dag)
	x, y := 0, 0
	np := DAGToNodePipeline(dag, &x, &y)
	ngraph := NodeGraph{
		Media:   "gstreamer",
		AppType: "gst",
		AppName: "NVR",
		Graph:   np,
	}
	t.Logf("++++++++++++\n")
	ngbytes, err := json.Marshal(ngraph)
	if err != nil {
		t.Fatalf("Unexpected error marshalling: %v", err)
	}
	t.Logf("parsed NodeGraph: %v", string(ngbytes))
}
