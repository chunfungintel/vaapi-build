package converter

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"testing"
)

func TestPipeline_Converter_Online_Pipeline_JSON(t *testing.T) {
	jsonFile, err := os.Open("../test_data/online-pipeline.json")
	if err != nil {
		t.Fatalf("Unexpected error opening json file: %v", err)
	}
	defer jsonFile.Close()

	jsonBytes, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		t.Fatalf("Unexpected error reading json file: %v", err)
	}

	var graph NodeGraph

	if err := json.Unmarshal(jsonBytes, &graph); err != nil {
		t.Fatalf("Unexpected error unmarshalling json: %v", err)
	}

	dag, err := NodeGraphToDAG(&graph)
	if err != nil {
		t.Fatalf("Unexpected error converting to DAG: %v", err)
	}

	str := DAGToString(dag)
	t.Logf("DAG from NodeGraph:\n%v", str)
}
