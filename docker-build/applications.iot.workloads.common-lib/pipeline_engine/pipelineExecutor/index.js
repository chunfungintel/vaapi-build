var express = require('express');
var logger = require('morgan');
var cors = require('cors');
var http = require('http');
var cookieParser = require('cookie-parser');

var app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(logger('dev')); // Log requests to API using morgan
app.use(cors());
app.use(cookieParser());

process.title = "plExec"

var pe = require("./pipeline-executor");

var router = express.Router();
var tempId = process.env.MqttTopic || "/nvr/p1";
tempId = tempId.split("/").pop();
var instId = tempId.substring(1);
var portNo = 38080;
if(tempId.indexOf('m') >= 0) {
    portNo = 38080 + parseInt(instId);
}

app.use('/', router);

// Get all pipelines
app.get('/', function (req, res) {
    res.status(200).json(pe.get());
});

router.post('/set', async function (req, res, next) {
    try {
        if(req.body.config) {
            pe.setConfig(req.body.config);
            return res.status(200).end();
        }
        else
            return next("invalid testname");
    } catch (err) {
        return next(err.toString());
    }
});

router.post('/add', async function (req, res, next) {
    try {
        if(req.body.pipeline) {
            await pe.add(req.body.pipeline);
            return res.status(200).end();
        } else
            return next("invalid pipeline");
    } catch (err) {
        return next("invalid pipeline");
    }
});

router.post('/run', async function (req, res, next) {
    try {
        pe.run();
        return res.status(200).end();
    } catch (err) {
        return next(err.toString());
    }
});

router.post('/stop', async function (req, res, next) {
    try {
        await pe.stop();
        return res.status(200).end();
    } catch (err) {
        return next(err.toString());
    }
});

router.post('/exit', async function (req, res, next) {
    try {
        await pe.stop();
        res.status(200).end();
        process.exit(0);
    } catch (err) {
        return next(err.toString());
    }
});

var httpServer = http.createServer(app);
httpServer.listen(portNo, () => {
    console.log("pipeline executor listen on ", portNo);
});
