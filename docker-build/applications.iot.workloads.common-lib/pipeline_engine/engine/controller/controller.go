package controller

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"text/template"

	"github.com/google/uuid"
	utils "github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/utils"
)

type (
	Element struct {
		ID          string          `json:"-"`
		Name        string          `json:"name"`
		ElementName string          `json:"elementName"`
		Parameters  string          `json:"parameters"`
		Input       json.RawMessage `json:"input,omitempty"`
		Output      json.RawMessage `json:"output,omitempty"`
		Duplicate   string          `json:"duplicate,omitempty"` // can NOT use int here due to placeholder
		Type        string          `json:"type,omitempty"`
	}

	KPI struct {
		Name    string `json:"name"`
		Type    string `json:"type"`
		Keyword string `json:"keyword"`
	}

	SubPipeline struct {
		ID       string    `json:"-"`
		Elements []Element `json:"elements"`
		Cmd      string    `json:"cmd,omitempty"`
	}

	Pipeline struct {
		Name         string                 `json:"name"`
		KPIs         []KPI                  `json:"kpi"`
		Values       map[string]string      `json:"values"`
		Elements     []Element              `json:"elements"`
		SubPipelines map[string]SubPipeline `json:"subPipelines"`
	}

	Replaceable struct {
		Values map[string]string `json:"values"`
		Env    map[string]string `json:"env"`
	}

	WorkloadConfig struct {
		Name string `json:"name"`
	}

	WorkloadPipeline struct {
		Name     string            `json:"name"`
		Type     string            `json:"type"`
		Config   map[string]string `json:"config"`
		Pipeline *Pipeline         `json:"pipeline,omitempty"`
	}

	Workload struct {
		Config    WorkloadConfig     `json:"config"`
		Pipelines []WorkloadPipeline `json:"pipelines"`
	}

	PipelineLoader interface {
		Load(typ, name string) (*Pipeline, error)
	}
)

const (
	EnvOld           = "{{env."
	EnvNew           = "{{.Env."
	ValueOld         = "{{values."
	ValueNew         = "{{.Values."
	singleSpace      = " "
	indexPlaceholder = "##index##"
	TypeSubPipeline  = "subPipeline"
	TypeElement      = "element"
)

func NewElementID() string {
	return uuid.NewString()
}

func (el *Element) UnmarshalJSON(data []byte) error {
	type elementAlias Element
	a := &elementAlias{
		ID: uuid.NewString(),
	}

	if err := json.Unmarshal(data, a); err != nil {
		return err
	}

	*el = Element(*a)
	return nil
}

func (sp *SubPipeline) UnmarshalJSON(data []byte) error {
	type spAlias SubPipeline
	a := &spAlias{
		ID: uuid.NewString(),
	}

	if err := json.Unmarshal(data, a); err != nil {
		return err
	}

	*sp = SubPipeline(*a)
	return nil
}

// ParseWorkload parse workload pipelines with envar and values.
// Pipeline is attached to WorkloadPipeline after parsing.
func ParseWorkload(workload *Workload, envars map[string]string, loader PipelineLoader) error {
	for i, wp := range workload.Pipelines {
		// load Pipeline
		p, err := loader.Load(wp.Type, wp.Name)
		if err != nil {
			return err
		}
		// set config to values
		for k, v := range wp.Config {
			p.Values[k] = v
		}
		// parse pipeline
		if err := ParsePipeline(p, envars); err != nil {
			return err
		}

		// TODO: no update required for Config?
		wp.Config = nil
		wp.Pipeline = p
		workload.Pipelines[i] = wp
	}
	return nil
}

// ParsePipeline parse pipeline with envar and values.
// Pipeline is updated.
func ParsePipeline(pipeline *Pipeline, envars map[string]string) error {
	// parse value first to replace envar
	// TODO: pipeline.Values only include envar?
	b, err := json.Marshal(&pipeline.Values)
	if err != nil {
		return err
	}
	r, err := parse(string(b), Replaceable{
		Values: pipeline.Values,
		Env:    envars,
	})
	if err != nil {
		return err
	}

	var newValues map[string]string
	if err := json.Unmarshal([]byte(r), &newValues); err != nil {
		return err
	}

	// TODO: no update required for Values?
	pipeline.Values = nil

	// parse other parts
	d, err := json.Marshal(pipeline)
	if err != nil {
		return err
	}
	l, err := parse(string(d), Replaceable{
		Values: newValues,
		Env:    envars,
	})
	if err != nil {
		return err
	}

	if err := json.Unmarshal([]byte(l), pipeline); err != nil {
		return err
	}

	return nil
}

func auto() string {
	return indexPlaceholder
}

func parse(original string, rvalue Replaceable) (string, error) {
	// replace {{env. with {{.env.
	// replace {{values. with {{.values.
	// replace embeded values
	var (
		replaced string
		err      error
		tmpl     *template.Template
	)

	replaced = strings.ReplaceAll(original, EnvOld, EnvNew)
	replaced = strings.ReplaceAll(replaced, ValueOld, ValueNew)

	funcMap := template.FuncMap{
		"auto": auto,
	}

	tmpl, err = template.New("pipeline").Funcs(funcMap).Parse(replaced)
	if err != nil {
		return "", err
	}

	var b strings.Builder
	b.Grow(2 * len(original))

	err = tmpl.Execute(&b, rvalue)
	if err != nil {
		return "", err
	}

	return b.String(), nil
}

//lint:ignore U1000 Ignore unused function temporarily
func elementsToCmd(elements []Element, subPipelines map[string]SubPipeline) (string, error) {
	var (
		cmd         strings.Builder
		lastElement *Element
	)

	for i, e := range elements {
		if utils.IsEmpty(e.ElementName) {
			return "", fmt.Errorf("empty ElementName %v", e)
		}

		if typ, empty := utils.IsEmptyWithValue(e.Type); empty || typ == "element" {
			// no type or type is element
			// set default type to element
			elementCmd(&cmd, &e, lastElement, i == 0)
		} else {
			// type is subPipeline
			if typ == "subPipeline" {
				sp, exist := subPipelines[e.ElementName]
				if !exist {
					return "", fmt.Errorf("ElementName %s not in subPipelines", e.ElementName)
				}

				c, empty := utils.IsEmptyWithValue(sp.Cmd)
				if empty {
					return "", fmt.Errorf("empty Cmd for subPipeline %s", e.ElementName)
				}
				subPipelineCmd(&cmd, &e, lastElement, c)
			}
		}

		lastElement = &e
	}
	return cmd.String(), nil
}

func subPipelineCmd(cmd *strings.Builder, element, lastElement *Element, subPipelineCmd string) {
	size := 1
	// var size = 1;
	//                 if (element.hasOwnProperty('duplicate') && element.duplicate > 0) {
	//                     size = parseInt(element.duplicate);
	//                 }
	//                 for (var i = 0; i < size; i++) {
	//                     if (!element.hasOwnProperty('input')) {
	//                         cmd += " ! ";
	//                     } else {
	//                         if (element.input != null && (!lastElement.hasOwnProperty('name') || (
	//                             lastElement.hasOwnProperty('name') && element.input != lastElement.name))) {
	//                             cmd += " " + element.input + ". ! ";
	//                         }
	//                     }
	//                     cmd += subPipelines[element.elementName].cmd.replace(/##index##/g, i) + " ";
	//                 }
	dup, err := strconv.Atoi(element.Duplicate)
	if err != nil {
		dup = 0
	}
	if dup > size {
		size = dup
	}

	for i := 0; i < size; i++ {
		in, empty := utils.IsEmptyWithValue(string(element.Input))
		if empty {
			cmd.WriteString(singleSpace)
			cmd.WriteString("!")
			cmd.WriteString(singleSpace)
		} else {
			if n, emptyN := utils.IsEmptyWithValue(lastElement.Name); emptyN || n != in {
				cmd.WriteString(singleSpace)
				cmd.WriteString(in)
				cmd.WriteString(". !")
				cmd.WriteString(singleSpace)
			}
		}
		cmd.WriteString(strings.ReplaceAll(subPipelineCmd, indexPlaceholder, strconv.Itoa(i)))
		cmd.WriteString(singleSpace)
	}
}

func elementCmd(cmd *strings.Builder, element, lastElement *Element, first bool) {
	// if (!element.hasOwnProperty('input') && elements.indexOf(element) != 0) {
	// 	cmd += " ! ";
	// } else {
	// 	if (element.input != null && (!lastElement.hasOwnProperty('name') || (
	// 		lastElement.hasOwnProperty('name') && element.input != lastElement.name))) {
	// 		cmd += " " + element.input + ". ! ";
	// 	}
	// }

	in, empty := utils.IsEmptyWithValue(string(element.Input))
	if !empty || first {
		// input not empty or first
		if n, emptyN := utils.IsEmptyWithValue(lastElement.Name); emptyN || n != in {
			cmd.WriteString(singleSpace)
			cmd.WriteString(in)
			cmd.WriteString(". !")
			cmd.WriteString(singleSpace)
		}
	} else {
		cmd.WriteString(singleSpace)
		cmd.WriteString("!")
		cmd.WriteString(singleSpace)
	}

	cmd.WriteString(element.ElementName)
	cmd.WriteString(singleSpace)

	if n, empty := utils.IsEmptyWithValue(element.Name); !empty {
		cmd.WriteString("name=")
		cmd.WriteString(n)
		cmd.WriteString(singleSpace)
	}

	if n, empty := utils.IsEmptyWithValue(element.Parameters); !empty {
		cmd.WriteString(singleSpace)
		cmd.WriteString(n)
		cmd.WriteString(singleSpace)
	}

	if n, empty := utils.IsEmptyWithValue(string(element.Output)); !empty {
		cmd.WriteString(singleSpace)
		cmd.WriteString(fmt.Sprintf("! %s.", n))
		cmd.WriteString(singleSpace)
	}

}
