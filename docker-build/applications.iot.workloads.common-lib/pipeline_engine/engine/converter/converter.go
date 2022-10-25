package converter

import (
	"fmt"
	"log"
	"sort"
	"strings"

	"github.com/goombaio/dag"
	"github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/controller"
	"github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/utils"
)

type (
	Edge struct {
		NextNode     string `json:"nextNode"`
		SourceHandle string `json:"sourceHandle"`
		TargetHandle string `json:"targetHandle"`
	}

	Position struct {
		X float64 `json:"x"`
		Y float64 `json:"y"`
	}

	Node struct {
		Type       string            `json:"type"`
		Position   Position          `json:"position"`
		Parameters map[string]string `json:"params"`
		Edges      []Edge            `json:"edges"`
	}

	NodePipeline struct {
		Start []string        `json:"start"`
		Nodes map[string]Node `json:"nodes"`
	}

	NodeGraph struct {
		Media   string                  `json:"media_fw"`
		AppType string                  `json:"appType"`
		AppName string                  `json:"appName"`
		Graph   map[string]NodePipeline `json:"graph"`
	}

	Category string
)

const (
	initX   float64 = 100
	initY   float64 = 100
	offsetX float64 = 200
	offsetY float64 = 200

	// element category
	input          Category = "Input"
	decode         Category = "Decode"
	postProcess    Category = "Post-process"
	compose        Category = "Compose"
	detect         Category = "Detect"
	classify       Category = "Classify"
	watermark      Category = "Watermark"
	presentation   Category = "Presentation"
	encode         Category = "Encode"
	output         Category = "Output"
	custom         Category = "Custom"
	parse          Category = "Parsing"
	measurement    Category = "Measurement"
	queue          Category = "Queue"
	identity       Category = "Gst Clock Sync"
	gvatrack       Category = "Tracking"
	gvametaconvert Category = "Metadata"
)

func DAGToNodeGraph(workloadName string, workloadDAG map[string]*dag.DAG) (*NodeGraph, error) {
	ngraph := NodeGraph{
		Media:   "gstreamer",
		AppType: "gst",
		AppName: workloadName,
		Graph:   make(map[string]NodePipeline, 5*len(workloadDAG)),
	}

	i, yy := 0, 0
	for _, d := range workloadDAG {
		nps := DAGToNodePipeline(d, &i, &yy)
		for n, p := range nps {
			if _, exist := ngraph.Graph[n]; exist {
				panic(fmt.Sprintf("duplicate NodePipeline name %s", n))
			}
			ngraph.Graph[n] = p
		}
	}

	return &ngraph, nil
}

func DAGToNodePipeline(d *dag.DAG, pipelineIdx, yIdx *int) map[string]NodePipeline {
	groups := CountPipelines(d)
	numOfPipelines := len(groups)
	graph := make(map[string]NodePipeline, numOfPipelines)

	for i := *pipelineIdx; i < numOfPipelines; i++ {
		np := NodePipeline{Start: groups[i], Nodes: make(map[string]Node)}
		generateNodesForPipeline(&np, d, i, yIdx)
		name := fmt.Sprintf("pipeline%d", i)
		graph[name] = np
		*pipelineIdx += 1
	}

	return graph
}

func WorkloadToDAG(workload controller.Workload, loader controller.PipelineLoader) (map[string]*dag.DAG, error) {
	nameToDAGMap := make(map[string]*dag.DAG, len(workload.Pipelines))
	for _, wp := range workload.Pipelines {
		p, err := loader.Load(wp.Type, wp.Name)
		if err != nil {
			return nil, err
		}
		nameToDAGMap[p.Name] = PipelineToDAG(p)
	}
	return nameToDAGMap, nil
}

// assume subPipeline only used once in elements
func PipelineToDAG(pipeline *controller.Pipeline) *dag.DAG {
	// nameToVertexMap contains pipeline.SubPipelines and pipeline.Elements with name
	nameToVertexMap := make(map[string]Vertex, len(pipeline.Elements))
	pipelineDAG := dag.NewDAG()
	// process all subPipelines first
	processSubPipelines(pipeline.SubPipelines, nameToVertexMap, pipelineDAG)

	// to capture all element type for reference within subPipeline
	elementToVertexMap := make(map[string]Vertex, len(pipeline.Elements))

	// first loop, skip subPipeline type, only handle element type
	for _, e := range pipeline.Elements {
		if typ := utils.TrimSpace(e.Type); typ == controller.TypeSubPipeline {
			_, exist := pipeline.SubPipelines[utils.TrimSpace(e.ElementName)]
			if !exist {
				panic(fmt.Sprintf("ElementName %s not in subPipelines", e.ElementName))
			}
			// skip subPipeline
			continue
		}
		// handle element
		ev := processElement(&e, nameToVertexMap, pipelineDAG)
		elementToVertexMap[ev.ID()] = ev
	}

	// second loop, link all elements, subPipeline type + element type
	lastEnd := (*dag.Vertex)(nil)
	vertex := (Vertex)(nil)
	for _, e := range pipeline.Elements {
		if typ := utils.TrimSpace(e.Type); typ == controller.TypeSubPipeline {
			name := utils.TrimSpace(e.ElementName)
			vertex = nameToVertexMap[name]
		} else {
			vertex = elementToVertexMap[e.ID]
		}

		input, output := vertex.Input(), vertex.Output()
		start, end := vertex.Traverse()

		// input "null" NO link
		// input ""     link to lastVertex
		// input "xxx"  link to "xxx"
		if !utils.IsEmpty(input) {
			if input != utils.NullStr {
				if iv, ok := nameToVertexMap[input]; ok {
					// TODO: panic if input not found?
					_, ivEnd := iv.Traverse()
					lastEnd = ivEnd
				}
			} else {
				lastEnd = nil
			}
		}

		if lastEnd != nil {
			_ = pipelineDAG.AddEdge(lastEnd, start)
		}

		lastEnd = end

		evv := end.Value.(Vertex)
		log.Printf("link %s output [%s] <- end [%s]\n", utils.WithDefault(e.Name, e.ElementName), output, evv.Name())

		// handle output
		if !utils.IsEmpty(output) && output != utils.NullStr {
			if iv, ok := nameToVertexMap[output]; ok {
				log.Printf("\t[%s] <- [%s]\n", iv.Name(), evv.Name())
				// TODO: panic if output not found?
				ivStart, _ := iv.Traverse()
				_ = pipelineDAG.AddEdge(end, ivStart)
			}
		}
	}

	removeTeeNode(pipelineDAG)

	return pipelineDAG
}

func CountPipelines(d *dag.DAG) [][]string {
	sv := d.SourceVertices()

	if len(sv) == 0 {
		panic("empty DAG")
	}

	if len(sv) == 1 {
		g := make([][]string, 1)
		g[0] = []string{sv[0].ID}
		return g
	}

	ord := d.Order()
	allSource := make(map[string]*dag.Vertex, len(sv))
	connected := make(map[string][]string, len(sv))
	connectedArr := make([]string, 0, len(sv))
	for _, v := range sv {
		allSource[v.ID] = v
		connected[v.ID] = make([]string, 0, len(sv))
		connectedArr = append(connectedArr, v.ID)
	}

	for i := 0; i < len(sv)-1; i++ {
		visited := make(map[string]struct{}, ord)
		walkSuccessors(d, sv[i], visited, nil, 1)
		log.Printf("start: %v", sv[i].ID)
		for j := i + 1; j < len(sv); j++ {
			if walkSuccessors(d, sv[j], visited, nil, 1) {
				connected[sv[i].ID] = append(connected[sv[i].ID], sv[j].ID)
			}
		}
	}

	sort.Slice(connectedArr, func(i, j int) bool {
		return len(connected[connectedArr[i]]) > len(connected[connectedArr[j]])
	})

	log.Printf("connected: %#v", connected)
	// log.Printf("connectedArr: %#v", connectedArr)

	groups := make([][]string, 0, len(sv))
	for _, start := range connectedArr {
		linked := connected[start]
		if _, exist := allSource[start]; !exist {
			continue
		}
		delete(allSource, start)
		group := make([]string, 0, len(sv))
		group = append(group, start)
		walkLinked(linked, connected, allSource, &group)
		groups = append(groups, group)
	}

	log.Printf("groups: %#v", groups)
	for _, v := range sv {
		log.Printf("%s -> %s", v.ID, v.Value.(Vertex).Name())
	}

	return groups
}

func removeTeeNode(d *dag.DAG) {
	sv := d.SourceVertices()
	if len(sv) == 0 {
		return
	}

	visited := make(map[string]struct{}, d.Order())
	callbk := func(v *dag.Vertex, x int) {
		vv := v.Value.(Vertex)
		if vv.ElementName() == "tee" {
			pred, _ := d.Predecessors(v)
			succ, _ := d.Successors(v)
			if err := d.DeleteVertex(v); err != nil {
				panic(fmt.Sprintf("failed to delete vertex %s", vv.Name()))
			}
			_ = d.DeleteEdge(pred[0], v)
			if len(pred) != 0 {
				for _, s := range succ {
					_ = d.DeleteEdge(v, s)
					_ = d.AddEdge(pred[0], s)
				}
			}
		}

		if strings.HasPrefix(vv.ElementName(), "video/x-raw") {
			vv.SetElementName("capsfilter")
			v.Value = vv
		}

		if vv.ElementName() == "gvametapublish" {
			pred, _ := d.Predecessors(v)
			for _, p := range pred {
				vv0 := p.Value.(Vertex)
				if vv0.ElementName() == "gvametaconvert" {
					vv0.SetParameter("publish", "true")
					vv0.SetParameter("method", vv.Parameters()["method"])
					vv0.SetParameter("file-path", vv.Parameters()["file-path"])
					p.Value = vv0

					// delete gvametapublish
					pred, _ := d.Predecessors(v)
					succ, _ := d.Successors(v)
					if err := d.DeleteVertex(v); err != nil {
						panic(fmt.Sprintf("failed to delete vertex %s", vv.Name()))
					}
					_ = d.DeleteEdge(pred[0], v)
					if len(pred) != 0 {
						for _, s := range succ {
							_ = d.DeleteEdge(v, s)
							_ = d.AddEdge(pred[0], s)
						}
					}
				}
			}
		}
	}
	for _, v := range sv {
		walkSuccessors(d, v, visited, callbk, 1)
	}
}

func elementNameToCategory(elementName, name string, params map[string]string) Category {
	if strings.HasPrefix(elementName, "video/x-raw") || strings.HasPrefix(elementName, "capsfilter") {
		return presentation
	}

	if strings.HasSuffix(elementName, "parse") {
		return parse
	}

	if strings.HasSuffix(elementName, "enc") {
		return encode
	}

	if strings.HasPrefix(elementName, "va") && strings.HasSuffix(elementName, "dec") {
		return decode
	}

	if strings.HasPrefix(elementName, "avdec_h") {
		return decode
	}

	switch elementName {
	case "multifilesrc", "rtspsrc", "rtpjitterbuffer", "rtph264depay":
		return input
	case "queue":
		return queue
	case "identity":
		return identity
	case "gvatrack":
		return gvatrack
	case "gvametaconvert": // "gvametapublish", publish=true|false
		return gvametaconvert
	case "vapostproc", "videoscale":
		return postProcess
	case "vacompositor", "compositor":
		return compose
	case "gvadetect":
		return detect
	case "gvaclassify":
		return classify
	case "gvawatermark":
		return watermark
	case "fakevideosink", "multifilesink", "kmssink", "fakesink":
		return output
	case "tee", "gvapython", "crypto", "bps", "jpegenc", "gva_crop":
		return custom
	default:
		panic(fmt.Sprintf("unknow elementNameToCategory %s", elementName))
	}
}

func generateNodesForPipeline(nodes *NodePipeline, d *dag.DAG, nPipeline int, yy *int) {
	visited := make(map[string]struct{}, d.Order())
	callbk := func(v *dag.Vertex, x int) {
		node := Node{
			Position:   Position{},
			Parameters: make(map[string]string),
		}
		vv := v.Value.(Vertex)
		parameters := vv.Parameters()
		if parameters != nil {
			node.Parameters = parameters
		}

		node.Type = string(elementNameToCategory(vv.ElementName(), vv.Name(), parameters))

		s, _ := d.Successors(v)
		if len(s) != 0 {
			node.Edges = make([]Edge, 0, len(s))
			for _, sv := range s {
				node.Edges = append(node.Edges, Edge{NextNode: sv.ID})
			}
		}

		// X = init + i*offset
		// Y = init + (nPipeline+y)*offset
		p, _ := d.Predecessors(v)
		y := max(len(p), len(s))
		node.Position.X = initX + float64(x)*offsetX
		node.Position.Y = initY + offsetY*float64(nPipeline+y+*yy)

		nodes.Nodes[v.ID] = node
	}

	for _, s := range nodes.Start {
		*yy += 1
		v, err := d.GetVertex(s)
		if err != nil {
			panic(err)
		}
		walkSuccessors(d, v, visited, callbk, 1)
	}
}

func walkLinked(linked []string, connected map[string][]string,
	allSource map[string]*dag.Vertex, group *[]string) {
	if len(linked) == 0 {
		return
	}
	for _, l := range linked {
		delete(allSource, l)
		*group = append(*group, l)
		al := connected[l]
		walkLinked(al, connected, allSource, group)
	}
}

func walkSuccessors(d *dag.DAG, vertex *dag.Vertex, visited map[string]struct{}, callbk func(*dag.Vertex, int), x int) bool {
	if _, exist := visited[vertex.ID]; exist {
		return true
	}
	visited[vertex.ID] = struct{}{}

	if callbk != nil {
		callbk(vertex, x)
	}

	s, _ := d.Successors(vertex)
	if len(s) == 0 {
		return false
	}

	for _, sv := range s {
		if walkSuccessors(d, sv, visited, callbk, x+1) {
			return true
		}
	}
	return false
}

func DAGToString(d *dag.DAG) string {
	var b strings.Builder
	b.Grow(1000)

	b.WriteString(fmt.Sprintf("DAG Vertices: %d - Edges: %d\n", d.Order(), d.Size()))
	b.WriteString("Vertices:\n")
	for _, sv := range d.SourceVertices() {
		svv := sv.Value.(Vertex)
		b.WriteString(fmt.Sprintf("\t%s\n", svv.Name()))
		b.WriteString("\tEdges:\n")
		printSuccessors(d, sv, 2, &b)
	}

	return b.String()
}

func printSuccessors(d *dag.DAG, vertex *dag.Vertex, i int, b *strings.Builder) {
	s, _ := d.Successors(vertex)
	if len(s) == 0 {
		return
	}

	v := vertex.Value.(Vertex)
	for _, sv := range s {
		vv := sv.Value.(Vertex)
		for j := 0; j < i; j++ {
			b.WriteString("\t")
		}
		b.WriteString(fmt.Sprintf("%v -> %v\n", v.Name(), vv.Name()))
		printSuccessors(d, sv, i+1, b)
	}
}

// assume referred element name appears earlier in the elements list
func processSubPipelines(subPipelines map[string]controller.SubPipeline, nameToVertexMap map[string]Vertex, pipelineDAG *dag.DAG) {
	for spName, sp := range subPipelines {
		if _, ok := nameToVertexMap[spName]; ok {
			panic(fmt.Sprintf("duplicated subPipeline name %s", spName))
		}
		spVertext := NewSubPipelineVertex(sp.ID, spName, "", "")
		// to capture element name for reference within subPipeline via element input field
		elementNameToVertexMap := make(map[string]*dag.Vertex, len(sp.Elements))
		lastVertex := (*dag.Vertex)(nil)
		// loop subPipeline elements
		for i, e := range sp.Elements {
			name := fmt.Sprintf("%s#%s", spName, utils.WithDefault(e.Name, e.ElementName))
			input, output := utils.ToString(e.Input), utils.ToString(e.Output)

			ev := NewElementVertex(e.ID, name, input, output, e.Parameters, e.ElementName, spName)
			v := dag.NewVertex(ev.ID(), ev)
			pipelineDAG.AddVertex(v)
			// unique name is required for reference
			if s, empty := utils.IsEmptyWithValue(e.Name); !empty {
				if _, ok := elementNameToVertexMap[s]; ok {
					panic(fmt.Sprintf("duplicated element name %s in subPipeline %s", s, spName))
				}
				elementNameToVertexMap[s] = v
			}

			// first element's input is subPipeline's input
			if i == 0 {
				spVertext.input = input
				log.Printf("%s input %s\n", spName, input)
				spVertext.start = v
			}
			// last element's output is subPipeline's output
			if i == len(sp.Elements)-1 {
				spVertext.output = output
				log.Printf("%s output %s\n", spName, output)
				spVertext.end = v
			}

			// input "null" NO link
			// input ""     link to lastVertex
			// input "xxx"  link to "xxx"
			if !utils.IsEmpty(input) {
				if input != utils.NullStr {
					if iv, ok := elementNameToVertexMap[input]; ok {
						// TODO: panic if input not found?
						lastVertex = iv
					}
				} else {
					lastVertex = nil
				}
			}

			if lastVertex != nil {
				vv := lastVertex.Value.(Vertex)
				log.Printf("%s AddEdge %s -> %s\n", spName, vv.Name(), name)
				_ = pipelineDAG.AddEdge(lastVertex, v)
			}

			lastVertex = v
		}

		// add for reference in subPipeline elements
		nameToVertexMap[spName] = spVertext
	}
}

func processElement(e *controller.Element, nameToVertexMap map[string]Vertex, pipelineDAG *dag.DAG) Vertex {
	input, output := utils.ToString(e.Input), utils.ToString(e.Output)

	ev := NewElementVertex(e.ID, e.Name, input, output, e.Parameters, e.ElementName)
	v := dag.NewVertex(ev.ID(), ev)
	pipelineDAG.AddVertex(v)
	ev.startEnd = v
	// unique name is required for reference
	if s, empty := utils.IsEmptyWithValue(e.Name); !empty {
		if _, ok := nameToVertexMap[s]; ok {
			panic(fmt.Sprintf("duplicated element name %s", s))
		}
		nameToVertexMap[s] = ev
	}
	return ev
}

func max(is ...int) int {
	l := len(is)
	if l == 0 {
		panic("empty param")
	}
	if l == 1 {
		return is[0]
	}

	i := is[0]
	for j := 1; j < l; j++ {
		if is[j] > i {
			i = is[j]
		}
	}
	return i
}
