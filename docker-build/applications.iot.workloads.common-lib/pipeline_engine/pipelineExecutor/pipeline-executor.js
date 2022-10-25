const fs = require('fs');
const jsonParse = require("json-templates");
require("util").inspect.defaultOptions.depth = null;
const { spawn } = require('child_process');

var mqtt = require("./wlc-mqtt");
mqtt.connect();

var testStop = true;
var tempId = process.env.MqttTopic || "/nvr/1";
tempId = tempId.split("/").pop();
var instId = tempId.substring(1);
var env = {
    outputDir: process.env.outputDir || "/home/kpi/output/results",
    datasetsDir: process.env.datasetsDir || "/home/kpi/datasets",
    MqttTopic: process.env.MqttTopic || "/nvr/1",
    RTSPSrc: process.env.RTSPSrc || "10.226.76.62:8080",
    instanceID: instId,
};

var config = {};

if (env.outputDir && (!fs.existsSync(env.outputDir))) {
    fs.mkdirSync(env.outputDir);
}

var outputStorage = env.outputDir + "/encryptStorage";
if (!fs.existsSync(outputStorage)) {
    fs.mkdirSync(outputStorage);
}

var outputLogs = env.outputDir + "/logs";
if (!fs.existsSync(outputLogs)) {
    fs.mkdirSync(outputLogs);
}

var outputVaMeta = env.outputDir + "/videoAnalytics";
if (!fs.existsSync(outputVaMeta)) {
    fs.mkdirSync(outputVaMeta);
}

var pipelines = [];

function elementsToCmd(elements, subPipelines) {
    return new Promise((resolve, reject) => {
        var cmd = " ";
        var lastElement = null;
        for (var element of elements) {

            if (!element.hasOwnProperty('elementName')) {
                console.log('elementName not exist');
                return reject();
            }

            if (element.hasOwnProperty('type') && element.type != "element") {
                if (element.type == 'subPipeline') {
                    var size = 0;

                    if (element.hasOwnProperty('duplicate') && element.duplicate > 0) {
                        size = parseInt(element.duplicate);
                    }
                    for (var i = 0; i < size; i++) {
                        if (!element.hasOwnProperty('input')) {
                            cmd += " ! ";
                        } else {
                            if (element.input != null && (!lastElement.hasOwnProperty('name') || (lastElement.hasOwnProperty('name') && element.input != lastElement.name))) {
                                cmd += " " + element.input + ". ! ";
                            }
                        }

                        if (!subPipelines.hasOwnProperty(element.elementName)) {
                            return reject();
                        }

                        if (!subPipelines[element.elementName].hasOwnProperty('cmd')) {
                            return reject();
                        }

                        cmd += subPipelines[element.elementName].cmd.replace(/##index##/g, i) + " ";
                    }
                }
            } else {
                if (!element.hasOwnProperty('input') && elements.indexOf(element) != 0) {
                    cmd += " ! ";
                } else {
                    if (element.input != null && (!lastElement.hasOwnProperty('name') || (lastElement.hasOwnProperty('name') && element.input != lastElement.name))) {
                        cmd += " " + element.input + ". ! ";
                    }
                }

                cmd += element.elementName + " ";

                if (element.hasOwnProperty('name')) {
                    cmd += "name=" + element.name + " ";
                }

                if (element.hasOwnProperty('parameters')) {
                    cmd += " " + element.parameters + " ";
                }

                if (element.hasOwnProperty('output') && element.output != null) {
                    cmd += " ! " + element.output + ". ";
                }

            }

            lastElement = element;
        }

        resolve(cmd);
    });
}

async function parser(pipeline) {
    return new Promise(async (resolve, reject) => {
        var template = jsonParse(pipeline.values);
        var values = template({ env: env });
        template = jsonParse(pipeline);
        pipeline = template({ env: env, values: values, configs: config, auto: "##index##" });

        for (var field in pipeline.subPipelines) {
            var subPipeline = pipeline.subPipelines[field];
            try {
                pipeline.subPipelines[field].cmd = await elementsToCmd(subPipeline.elements, pipeline.subPipelines);
            } catch (err) {
                return reject();
            }
        }

        elementsToCmd(pipeline.elements, pipeline.subPipelines).then(cmd => {
            return resolve(cmd);
        }).catch(() => reject());

    });
}

async function add(pipeline) {
    return new Promise((resolve, reject) => {
        parser(pipeline).then((cmd) => {
            var p = { name: pipeline.name, values: pipeline.values, cmd: cmd, kpi: pipeline.kpi, status: "Ready", proc: null };
            if(pipeline.values.hasOwnProperty('G_density_category'))
                p.density = pipeline.values.G_density_category;
            pipelines.push(p);
            if(pipeline.values.hasOwnProperty('G_MonitorName'))
                p.monitor = pipeline.values.G_MonitorName;
            pipelines.push(p);
            //console.log(pipelines);
            resolve();
        }).catch(() => reject());
    });
}
exports.add = add;

function get() {
    var ret = [];
    pipelines.forEach(p => {
        ret.push({
            name: p.name,
            //cmd: p.cmd,
            kpi: p.kpi,
            status: p.status
        });
    });

    return ret;
}
exports.get = get;

var kpiResult = {};

function kpiPostProcess(pipeline, log) {
    lines = log.replace(/\r\n/g, '\n').split('\n');

    pipeline.kpi.forEach(kpi => {
        if (!kpi.hasOwnProperty('value')) kpi.value = 0;
        if (!kpi.hasOwnProperty('count')) kpi.count = 0;
    });

    // post process kpi results
    lines.forEach(line => {
        pipeline.kpi.forEach(kpi => {
            if (kpi.type === "bps" && line.includes(kpi.keyword) && line.includes("current bps:")) {
                var Regex = /current bps: ([0-9]+\.[0-9]+)/
                if(line.match(Regex)[1]) {
                    kpi.value += parseFloat(line.match(Regex)[1]);
                    kpi.count++;
                }
            } else if (kpi.type === "theo" && line.includes(kpi.keyword) && line.includes("current bps:")) {
                var Regex = /current bps: ([0-9]+\.[0-9]+)/
                if(line.match(Regex)[1]) {
                    kpi.value += parseFloat(line.match(Regex)[1]);
                    kpi.count++;
                }
            } else if (kpi.type === 'ips' && line.includes(`model_name: ${kpi.model_name}`)) {
                var Regex = / inference size: ([0-9]+)/
                kpi.value += parseFloat(line.match(Regex)[1]);

                Regex = /0:([0-9]+:[0-9]+.[0-9]+) /
                var str = line.match(Regex)[1].split(":");
                var min = parseInt(str[0]);
                str = str[1].split(".");
                var sec = parseInt(str[0]);
                var ms = parseInt(str[1].slice(0, 3));
                var timeStamp = min * 60 * 1000 + sec * 1000 + ms;
                if (!kpi.hasOwnProperty('start')) {
                    kpi.start = timeStamp;
                    kpi.count = 0;
                } else {
                    kpi.count = parseFloat(((timeStamp - kpi.start) / 1000));
                }
            }
        });
    });

    var va_stream_count = 0;
    if (pipeline.values.hasOwnProperty('G_NumofVaStream') && parseInt(pipeline.values.G_NumofVaStream) > 0){
        va_stream_count = parseInt(pipeline.values.G_NumofVaStream);
    }
    var theo_pipeline_count = 1;
    if (pipeline.values.hasOwnProperty('G_num_theo_pipelines') && parseInt(pipeline.values.G_num_theo_pipelines) > 0){
        theo_pipeline_count = parseInt(pipeline.values.G_num_theo_pipelines);
    }
    if (pipeline.values.hasOwnProperty('G_NumofVaStream'))
    {
        kpiResult['No. of VAs'] = { value: va_stream_count, count: 1 };
    }

    pipeline.kpi.forEach(kpi => {
        kpi.result = (kpi.value / kpi.count).toFixed(2);
        var stream_count = 1;
        if (kpi.type === 'ips') {
            if (kpi.hasOwnProperty("stream_count") && parseInt(kpi.stream_count) > 0) {
                stream_count = parseInt(kpi.stream_count);
            }
            if (va_stream_count > 0)
            {
                stream_count = va_stream_count*stream_count;
            }
            kpi.result = (kpi.result / stream_count).toFixed(2);
        }
        if (kpi.type === 'theo') {
            kpi.result = (kpi.result * theo_pipeline_count / 30.0).toFixed(2);
            stream_count = (30 / theo_pipeline_count).toFixed(2);
        }
        fs.appendFileSync(`${outputLogs}/perf.log`, `${pipeline.name}-${kpi.name}: ${kpi.result}\n`);

        if (kpiResult[kpi.name])
            kpiResult[kpi.name] = {
                value: kpi.value / stream_count + kpiResult[kpi.name].value,
                count: kpi.count + kpiResult[kpi.name].count
            };
        else
            kpiResult[kpi.name] = { value: kpi.value / stream_count, count: kpi.count };
    });
}


function runPipeline(pipeline) {
    return new Promise((resolve, reject) => {
        var cmd = "python3";
        var plcmd = "\""+pipeline.cmd+"\"";
        var args = ["dlm-gst-run.py", plcmd];

        if (pipeline.hasOwnProperty('monitor'))
            args.push(pipeline.monitor);

        var options = {
            shell: true,
            env: {
                ...process.env,
                GST_DEBUG: 'bps:4,GVA_common:3',
                //ENABLE_GVA_FEATURES: 'vaapi-preproc-yuv,disable-tensor-copying',
            }
        }

        //density test does not require bps/ips logs, off it to reduce RAM usage of each container
        if (pipeline.hasOwnProperty('density') && pipeline.density == '1')
            options.env.GST_DEBUG=""

        if (pipeline.values.hasOwnProperty('G_num_theo_pipelines') && parseInt(pipeline.values.G_num_theo_pipelines) > 0)
            options.env.GST_DEBUG="bps:4"

        var proc = spawn(cmd, args, options);
        pipeline.proc = proc;

        //var output = 'cmd: ' + str + '\n---- stdout ----\n';
        var output = '---- stdout ----\n';
        var errmsg = '---- stderr ----\n';

        proc.stdout.setEncoding('utf8');
        proc.stderr.setEncoding('utf8');

        //console.log(pipeline.cmd);

        proc.stdout.on('data', (data) => {
            console.log(`${data}`);
            if (!(pipeline.hasOwnProperty('density') && pipeline.density == '1'))
                output += data;
        });

        proc.stderr.on('data', (data) => {
            console.log(`${data}`);
            if (!(pipeline.hasOwnProperty('density') && pipeline.density == '1'))
                errmsg += data;
        });

        proc.on('error', (err) => {
            console.log('error:', err);
            errmsg += err;
        });

        proc.on('close', (code) => {
            console.log(`pipeline ${pipeline.name} exited with code ${code}`);
            if (code != 0) {
                output += errmsg;
                //console.log(`errmsg: ${errmsg}`);
            }

            if (!testStop) {
                mqtt.send_lwt_msg();
            }

            pipeline.proc = null;
            pipeline.status = "Stop";

            // write log
            fs.writeFileSync(`${outputLogs}/${pipeline.name}.log`, output);

            kpiPostProcess(pipeline, output);
            resolve();
        });
    });
}

//todo: var aliveinterval;

async function run() {
    testStop = false;
    mqtt.send_connected_msg();
    return new Promise((resolve, reject) => {
        fs.writeFileSync(`${outputLogs}/perf.log`, `perf details : \n`);
        var PromisesArray = [];
        kpiResult = {};

        //todo: aliveinterval = setInterval(mqtt.send_keepalive_msg, 25000);

        pipelines.forEach(p => {
            if (p.status != "Running") {
                p.status = "Running";
                PromisesArray.push(runPipeline(p));
            }
        });

        Promise.all(PromisesArray).then(() => {
            fs.appendFileSync(`${outputLogs}/perf.log`, `\nperf summary :\n`);
            for (field in kpiResult) {
                var result = ((parseFloat(kpiResult[field].value)) / parseFloat(kpiResult[field].count)).toFixed(2);
                //console.log(kpiResult[field].value, kpiResult[field].count);
                console.log(`kpi - ${field}: ${result}`);
                fs.appendFileSync(`${outputLogs}/perf.log`, `${field}: ${result}\n`);
                mqtt.send_kpi_results(field, result);
            }

            mqtt.send_terminated_msg();
        });

        resolve();
    });
}
exports.run = run;

var kill = require('tree-kill');

async function stop() {
    testStop = true;
    return new Promise((resolve, reject) => {
        pipelines.forEach(p => {
            if (p.proc)
                kill(p.proc.pid);
                //p.proc.kill();
        });
        //todo: clearInterval(aliveinterval);
        resolve();
    });
}
exports.stop = stop;

function setTestName(name) {
    outputLogs = `${env.outputDir}/logs/${name}`;
    if (!fs.existsSync(outputLogs)) {
        fs.mkdirSync(outputLogs);
    }
}

function setConfig(conf) {
    if (conf.hasOwnProperty("name")) {
        setTestName(conf.name);
    }
    config = conf;
}
exports.setConfig = setConfig;
