package converter

import (
	"encoding/csv"
	"fmt"
	"strings"

	"github.com/goombaio/dag"
	"github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/utils"
)

type (
	Vertex interface {
		Name() string
		ID() string
		Input() string
		Output() string
		ElementName() string
		SetElementName(string)
		Parameters() map[string]string
		SetParameter(string, string)
		Traverse() (start *dag.Vertex, end *dag.Vertex)
	}

	ElementVertex struct {
		subPipeline string
		name        string
		elementName string
		id          string
		input       string
		output      string
		params      string
		startEnd    *dag.Vertex
	}

	SubPipelineVertex struct {
		name   string
		id     string
		input  string
		output string
		start  *dag.Vertex
		end    *dag.Vertex
	}
)

var (
	_ Vertex = (*ElementVertex)(nil)
	_ Vertex = (*SubPipelineVertex)(nil)
)

func NewElementVertex(id, name, input, output, params, elementName string, subPipelineName ...string) *ElementVertex {
	ev := &ElementVertex{name: name, id: id, input: input, output: output, params: params, elementName: elementName}
	if len(subPipelineName) > 0 {
		ev.subPipeline = subPipelineName[0]
	}
	return ev
}

func NewSubPipelineVertex(id, name, input, output string) *SubPipelineVertex {
	return &SubPipelineVertex{name: name, id: id,
		input: input, output: output}
}

func (e *ElementVertex) SetParameter(k, v string)  { e.params = fmt.Sprintf("%s %s=%s", e.params, k, v) }
func (e *ElementVertex) SetElementName(str string) { e.elementName = str }
func (e *ElementVertex) ElementName() string       { return e.elementName }
func (e *ElementVertex) Name() string              { return e.name }
func (e *ElementVertex) ID() string                { return e.id }
func (e *ElementVertex) Input() string             { return e.input }
func (e *ElementVertex) Output() string            { return e.output }
func (e *ElementVertex) Traverse() (start *dag.Vertex, end *dag.Vertex) {
	return e.startEnd, e.startEnd
}
func (e *ElementVertex) Parameters() map[string]string {
	p, err := parseParams(e.params)
	if err != nil {
		panic(err)
	}
	if !utils.IsEmpty(e.name) {
		p["name"] = e.name
	}
	if !utils.IsEmpty(e.elementName) {
		p["element-name"] = e.elementName
	}
	if !utils.IsEmpty(e.subPipeline) {
		p["subPipeline-name"] = e.subPipeline
	}
	return p
}

func (s *SubPipelineVertex) SetElementName(string) {}
func (s *SubPipelineVertex) ElementName() string   { return "" }
func (s *SubPipelineVertex) Name() string          { return s.name }
func (s *SubPipelineVertex) ID() string            { return s.id }
func (s *SubPipelineVertex) Input() string         { return s.input }
func (s *SubPipelineVertex) Output() string        { return s.output }
func (s *SubPipelineVertex) Traverse() (start *dag.Vertex, end *dag.Vertex) {
	return s.start, s.end
}
func (s *SubPipelineVertex) Parameters() map[string]string {
	return nil
}
func (s *SubPipelineVertex) SetParameter(string, string) {}

func parseParams(params string) (map[string]string, error) {
	if len(params) == 0 {
		return make(map[string]string), nil
	}

	var ss []string
	n := strings.Count(params, "=")
	switch n {
	case 0:
		return nil, fmt.Errorf("%s must be formatted as key=value", params)
	case 1:
		ss = append(ss, strings.Trim(params, `"`))
	default:
		r := csv.NewReader(strings.NewReader(params))
		r.Comma = ' '
		var err error
		ss, err = r.Read()
		if err != nil {
			return nil, err
		}
	}

	out := make(map[string]string, len(ss))
	for _, pair := range ss {
		kv := strings.SplitN(pair, "=", 2)
		if len(kv) != 2 {
			return nil, fmt.Errorf("%s must be formatted as key=value", pair)
		}
		out[kv[0]] = kv[1]
	}

	return out, nil
}
