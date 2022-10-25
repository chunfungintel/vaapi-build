package controller

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"path"
	"testing"

	"github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/utils"
)

func TestPipelineController_Read_Pipeline_JSON(t *testing.T) {
	jsonFile, err := os.Open("../test_data/pipelines/4k-videowall-vacomp-4kenc-pipeline.json")
	if err != nil {
		t.Fatalf("Unexpected error opening json file: %v", err)
	}
	defer jsonFile.Close()

	jsonBytes, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		t.Fatalf("Unexpected error reading json file: %v", err)
	}

	var pipeline Pipeline

	if err := json.Unmarshal(jsonBytes, &pipeline); err != nil {
		t.Fatalf("Unexpected error unmarshalling json: %v", err)
	}

	t.Logf("json: %v", pipeline)

	r, _ := json.Marshal(&pipeline)
	t.Logf("json: %v", string(r))
}

func TestPipelineController_Parse_Pipeline_JSON(t *testing.T) {
	jsonFile, err := os.Open("../test_data/pipelines/4k-videowall-vacomp-4kenc-pipeline.json")
	if err != nil {
		t.Fatalf("Unexpected error opening json file: %v", err)
	}
	defer jsonFile.Close()

	jsonBytes, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		t.Fatalf("Unexpected error reading json file: %v", err)
	}

	var pipeline Pipeline

	if err := json.Unmarshal(jsonBytes, &pipeline); err != nil {
		t.Fatalf("Unexpected error unmarshalling json: %v", err)
	}

	t.Logf("json: %v", pipeline)

	envars := make(map[string]string)
	envars["datasetsDir"] = "/usr/local/data"
	envars["outputDir"] = "/usr/local/output"

	if err := ParsePipeline(&pipeline, envars); err != nil {
		t.Fatalf("Unexpected error parsing json: %v", err)
	}

	for _, e := range pipeline.Elements {
		t.Logf("<<ID>>%s\n", e.ID)
		if utils.TrimSpace(e.ID) == "" {
			t.Fatalf("empty element ID: %v", e)
		}
	}

	for _, sp := range pipeline.SubPipelines {
		for _, e := range sp.Elements {
			if utils.TrimSpace(e.ID) == "" {
				t.Fatalf("empty element ID: %v", e)
			}
		}
	}

	r, err := json.Marshal(&pipeline)
	if err != nil {
		t.Fatalf("Unexpected error marshalling: %v", err)
	}
	t.Logf("parsed json: %v", string(r))
}

func TestPipelineController_Parse_Workload_JSON(t *testing.T) {
	jsonFile, err := os.Open("../test_data/nvr-adl-proxy-workload-h1-d-hevc-gpu.json")
	if err != nil {
		t.Fatalf("Unexpected error opening json file: %v", err)
	}
	defer jsonFile.Close()

	jsonBytes, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		t.Fatalf("Unexpected error reading json file: %v", err)
	}

	var workload Workload

	if err := json.Unmarshal(jsonBytes, &workload); err != nil {
		t.Fatalf("Unexpected error unmarshalling json: %v", err)
	}

	t.Logf("json: %v", workload)

	envars := make(map[string]string)
	envars["datasetsDir"] = "/usr/local/data"
	envars["outputDir"] = "/usr/local/output"

	if err := ParseWorkload(&workload, envars, filePipelineLoader{}); err != nil {
		t.Fatalf("Unexpected error parsing json: %v", err)
	}

	r, err := json.Marshal(&workload)
	if err != nil {
		t.Fatalf("Unexpected error marshalling: %v", err)
	}
	t.Logf("parsed json: %v", string(r))
}

type filePipelineLoader struct{}

func (fp filePipelineLoader) Load(typ, name string) (*Pipeline, error) {
	jsonFile, err := os.Open(path.Join("../test_data/pipelines/", name))
	if err != nil {
		return nil, err
	}
	defer jsonFile.Close()

	jsonBytes, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		return nil, err
	}

	var pipeline Pipeline

	if err := json.Unmarshal(jsonBytes, &pipeline); err != nil {
		return nil, err
	}
	return &pipeline, nil
}
