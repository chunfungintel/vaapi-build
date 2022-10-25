var request = require('request');
const fs = require('fs');

process.title = "plCont"

const ConfigPath = process.env.WKLD_CONFIG_PATH || "/home/kpi/config"

var configFile = process.env.WKLD_CONFIG || "nvr";
configFile = ConfigPath + "/" + configFile + ".yaml";

var config = {};

if (fs.existsSync(configFile)) {
    config = JSON.parse(fs.readFileSync(configFile));
    //console.log(config);
} else {
    console.log("Error: Config file not exist");
    /** todo send mqtt terminate msg */
    send_request('exit', {});
    process.exit(1);
}

var testsuit = process.env.TestSuit || config.TestSuit || 'invalid';
var testTimeout = process.env.TestTimeout || config.TestTimeout || -1;
var tempId = process.env.MqttTopic || "/nvr/p1";
tempId = tempId.split("/").pop();
var instId = tempId.substring(1);
var portNo = 38080;
if(tempId.indexOf('m') >= 0) {
    portNo = 38080 + parseInt(instId);
}

testTimeout = parseInt(testTimeout);

console.log("Info: Test start");
console.log("- TestSuit: " + testsuit);
console.log("- TestTimeout: " + testTimeout);

if (testsuit == 'invalid' || testTimeout == -1) {
    console.log("Error: Testsuit or testTimeout is not set");
    send_request('exit', {});
    process.exit(1);
}

var testcaseFile = `../workload-config/${testsuit}.json`;
if (!fs.existsSync(testcaseFile)) {
    console.log("Error: Testsuit is not found");
    send_request('exit', {});
    process.exit(1);
}

var testcase = JSON.parse(fs.readFileSync(testcaseFile));

var config = {
};

console.log("- Config: ", config);

function get_status() {
    return new Promise((resolve, reject) => {
        var options = {
            url: 'http://localhost:' + portNo.toString() + '/',
            method: 'GET',
            json: true,
            proxy: ''
        }

        request(options, function (error, response, body) {
            if (error) {
                console.log(error);
                reject(error);
            }
            //console.log(body);
            resolve();
        });
    });
}

function send_request(path, json) {
    return new Promise((resolve, reject) => {
        var options = {
            url: 'http://localhost:' + portNo.toString() + '/' + path,
            method: 'POST',
            json: json,
            proxy: ''
        }

        request(options, function (error, response, body) {
            if (error) {
                console.log(error);
                reject(error);
            }
            resolve();
        });
    });
}

async function main() {
    return new Promise(async (resolve, reject) => {
        try {
            await send_request('set', { config: testcase.config });

            for (var j = 0; j < testcase.pipelines.length; j++) {
                var p = testcase.pipelines[j];
                var duplicate = 1;
                if (p.duplicate)
                    duplicate = p.duplicate;

                if (p.type == 'file') {
                    var pipeline = require(`../workload-config/pipelines/${p.name}`);
                    for (var field in p.config) {
                        pipeline.values[field] = p.config[field];
                    }
                    for (var i = 0; i < duplicate; i++) {
                        await send_request('add', { pipeline: pipeline });
                    }
                } else {
                    for (var i = 0; i < duplicate; i++) {
                        await send_request('add', { pipeline: p });
                    }
                }
            };

            await get_status();
            await send_request('run', {});

            if (testTimeout > 0) {
            setTimeout(async () => {
                console.log("Info: Timeout, stopping...");
                await send_request('stop', {});
                resolve();
            }, testTimeout * 1000);
            }

        } catch (err) {
            console.log('Error: Fail to run test case!');
            reject();
        }
    });
}

main().then(() => {
    setTimeout(async () => {
        await send_request('exit', {});
        console.log('Info: Test completed!');
        process.exit(0);
    }, 10000); // wait for clean up then exit
});

let interval = setInterval(() => {}, 100000000);

process.on('SIGTERM', ()=>{
    clearInterval(interval);
    send_request('exit', {});
    process.exit(0);
});
