package converter

import (
	"errors"
	"strings"

	"github.com/goombaio/dag"
	"github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/controller"
	"github.com/intel-sandbox/virtualization.multios.edge-system.video-analytics.kubernetes-va-serving/utils"
)

const (
	singSpace          = " "
	teeElementName     = "tee"
	publishElementName = "gvametapublish"
)

var errDuplicateRecord = errors.New("duplicate pipeline node id")

func NodeGraphToDAG(ng *NodeGraph) (*dag.DAG, error) {
	nameToEdgeMap := make(map[string][]Edge)
	pipelineDAG := dag.NewDAG()

	for _, pipeline := range ng.Graph {
		for id, node := range pipeline.Nodes {
			ev := NewElementVertex(id, id, "", "", parameterMapToString(node.Parameters), utils.WithDefault(node.Parameters["element-name"], "default"))
			if _, exist := nameToEdgeMap[ev.ID()]; exist {
				return nil, errDuplicateRecord
			}
			v := dag.NewVertex(ev.ID(), ev)
			pipelineDAG.AddVertex(v)
			nameToEdgeMap[ev.ID()] = node.Edges
		}
	}

	// link nodes in DAG
	visited := make(map[string]struct{}, pipelineDAG.Order())
	for _, pipeline := range ng.Graph {
		for _, start := range pipeline.Start {
			linkNodesInEdges(start, nameToEdgeMap, pipelineDAG, visited)
		}
	}

	insertElementTee(pipelineDAG)

	return pipelineDAG, nil
}

func insertElementTee(d *dag.DAG) {
	sv := d.SourceVertices()
	visited := make(map[string]struct{}, d.Order())
	for _, v := range sv {
		addTeeToBranch(v, d, visited)
	}
}

func addTeeToBranch(v *dag.Vertex, d *dag.DAG, visited map[string]struct{}) {
	if _, ok := visited[v.ID]; ok {
		return
	}
	visited[v.ID] = struct{}{}

	succ, _ := d.Successors(v)

	vv := v.Value.(Vertex)
	if vv.ElementName() == "gvametaconvert" {
		if vv.Parameters()["publish"] == "true" {
			publish := NewElementVertex(controller.NewElementID(), "gvametapublish", "", "", "", publishElementName)
			publish.SetParameter("method", vv.Parameters()["method"])
			publish.SetParameter("file-path", vv.Parameters()["file-path"])
			publishV := dag.NewVertex(publish.ID(), publish)
			d.AddVertex(publishV)
			d.AddEdge(v, publishV)
			for _, s := range succ {
				d.DeleteEdge(v, s)
				d.AddEdge(publishV, s)
			}
		}
	}

	if len(succ) == 2 {
		tee := NewElementVertex(controller.NewElementID(), "tee", "", "", "", teeElementName)
		teeV := dag.NewVertex(tee.ID(), tee)
		d.AddVertex(teeV)
		d.DeleteEdge(v, succ[0])
		d.DeleteEdge(v, succ[1])
		d.AddEdge(v, teeV)
		d.AddEdge(teeV, succ[0])
		d.AddEdge(teeV, succ[1])
	}

	for _, s := range succ {
		addTeeToBranch(s, d, visited)
	}
}

func linkNodesInEdges(parent string, nameToEdgeMap map[string][]Edge, d *dag.DAG, visited map[string]struct{}) error {
	if _, ok := visited[parent]; ok {
		return nil
	}
	visited[parent] = struct{}{}

	edges := nameToEdgeMap[parent]
	if len(edges) == 0 {
		return nil
	}

	p, err := d.GetVertex(parent)
	if err != nil {
		return err
	}
	for _, edge := range edges {
		n, err := d.GetVertex(edge.NextNode)
		if err != nil {
			return err
		}
		if err := d.AddEdge(p, n); err != nil {
			return err
		}
		if err := linkNodesInEdges(edge.NextNode, nameToEdgeMap, d, visited); err != nil {
			return err
		}
	}

	return nil
}

func parameterMapToString(params map[string]string) string {
	b := strings.Builder{}
	b.Grow(len(params) * 50)

	for k, v := range params {
		b.WriteString(k)
		b.WriteString("=")
		b.WriteString(v)
		b.WriteString(singSpace)
	}

	return strings.TrimSuffix(b.String(), singSpace)
}
