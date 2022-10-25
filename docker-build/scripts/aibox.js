'use strict';

const fs = require('fs');
var path = require('path');

let rawdata = fs.readFileSync('/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json');
let data = JSON.parse(rawdata);
console.log(data);
console.log(data.subPipelines.aibox_low_pipeline_rtspsrc.elements.length);

/*
console.log(data.subPipelines.length);
for (var i=0; i<data.subPipelines.length; i++) {
console.log(i);
}

for (var i=0; i<data.subPipelines.aibox_low_pipeline_rtspsrc.elements.length; i++) {
if (data.subPipelines.aibox_low_pipeline_rtspsrc.elements[i].elementName == "vah264dec") {
    console.log(data.subPipelines.aibox_low_pipeline_rtspsrc.elements[i]);
}
}
*/

var pipelines = Object.keys(data.subPipelines);
for (var i = 0;i <pipelines.length;i++) { 
	console.log(pipelines[i]);
	var elements = Object.keys(data.subPipelines[pipelines[i]].elements);
	console.log(elements.length);
	for (var j=elements.length -1; j>=0; j--) {
		if( data.subPipelines[pipelines[i]].elements[j].elementName == "video/x-raw(memory:VAMemory),format=NV12") {
			data.subPipelines[pipelines[i]].elements[j].elementName = "video/x-raw,format=NV12";
			console.log(data.subPipelines[pipelines[i]].elements[j]);
		}
		if( data.subPipelines[pipelines[i]].elements[j].elementName == "video/x-raw,format=NV12,height=720,width=1280") {
			data.subPipelines[pipelines[i]].elements[j].elementName = "video/x-raw,format=NV12";
			console.log(data.subPipelines[pipelines[i]].elements[j]);
		}
		if( data.subPipelines[pipelines[i]].elements[j].elementName == "vah264dec") {
			data.subPipelines[pipelines[i]].elements[j].elementName = "vaapih264dec";
			console.log(data.subPipelines[pipelines[i]].elements[j]);
		}
		if( data.subPipelines[pipelines[i]].elements[j].elementName == "vah264lpenc") {
			data.subPipelines[pipelines[i]].elements[j].elementName = "vaapih264enc";
			delete data.subPipelines[pipelines[i]].elements[j].parameters;
			console.log(data.subPipelines[pipelines[i]].elements[j]);
		}
		if( data.subPipelines[pipelines[i]].elements[j].elementName == "vapostproc") {
			data.subPipelines[pipelines[i]].elements[j].elementName = "vaapipostproc";
			console.log(data.subPipelines[pipelines[i]].elements[j]);
		}
		if( data.subPipelines[pipelines[i]].elements[j].elementName == "gvawatermark") {
			//delete data.subPipelines[pipelines[i]].elements[j];
            data.subPipelines[pipelines[i]].elements.splice(j, 1);
			console.log(data.subPipelines[pipelines[i]].elements[j]);
		}
	}
}

//console.log(data);
let output = JSON.stringify(data, null, 2);
fs.writeFileSync('/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json', output);

/*
var test = {
  "result": [{
    "FirstName": "Test1",
    "LastName": "User"
  }, {
    "FirstName": "user",
    "LastName": "user"
  }, {
    "FirstName": "programmer",
    "LastName": "programmer"
  }]
}
for(var i=0; i <test.result.length; i++){
if (i == 0) {
delete test.result[i];
}
console.log(test.result[i]);
}
for(var i=0; i <test.result.length; i++){
console.log(test.result[i]);
}
*/

const pipelineFiles = [
"nvr-adl-measured-aibox-low-na-avc-cpu.json",
"nvr-adl-measured-aibox-low-na-avc-gpu.json",
"nvr-adl-measured-aibox-mid-na-avc-cpu.json",
"nvr-adl-measured-aibox-mid-na-avc-cpu.json",
"nvr-adl-proxy-aiboxTheo-low-na-avc-cpu.json",
"nvr-adl-proxy-aiboxTheo-low-na-avc-gpu.json",
"nvr-adl-proxy-aiboxTheo-mid-na-avc-cpu.json",
"nvr-adl-proxy-aiboxTheo-mid-na-avc-gpu.json"
];
pipelineFiles.forEach(file  => {
	fs.readFile(path.join('/home/kpi/workload/workload-config', file), (err, rawdata) => {
		var pipelineData = JSON.parse(rawdata);
		console.log(pipelineData.pipelines[0].config.T_pre_process_backend);
		pipelineData.pipelines[0].config.T_pre_process_backend = "auto";
		//console.log(pipelineData);
		let pipelineEdit = JSON.stringify(pipelineData, null, 2);
		fs.writeFileSync(path.join('/home/kpi/workload/workload-config', file), pipelineEdit);
	});
});



