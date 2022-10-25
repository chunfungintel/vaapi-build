const mqtt = require('mqtt')
var util = require('util');

var client;
var mqttBroker = process.env.MQTT_IP_ADDRESS || null;
var mqttPort = process.env.MQTT_PORT || 1883;
var mqttConnected = false;
var mqttTopic = process.env.MqttTopic || null;

const topic_status = "/kpi/status";
const topic_kpi = "/kpi/metric/%s/value";

function connect() {
    if (!mqttTopic || !mqttBroker) {
        console.log("Warnning: invalid Mqtt Topic or Mqtt Broker, skip send mqtt msg");
    } else {
        client = mqtt.connect(`mqtt://${mqttBroker}:${mqttPort}`);
        client.on('connect', function () {
            console.log("mqtt connected");
            mqttConnected = true;
        });
    }
}
exports.connect = connect;

function send_connected_msg() {
    if (mqttConnected) {
        client.publish(mqttTopic + topic_status, JSON.stringify({
            timestamp: Date.now(),
            message: "connected"//todo: ,
            //todo: keep_alive_window: 28
        }));
    }
}
exports.send_connected_msg = send_connected_msg;

function send_terminated_msg() {
    if (mqttConnected) {
        client.publish(mqttTopic + topic_status, JSON.stringify({
            timestamp: Date.now(),
            message: "terminated"
        }));
    }
}
exports.send_terminated_msg = send_terminated_msg;

function send_lwt_msg() {
    if (mqttConnected) {
        client.publish(mqttTopic + topic_status, JSON.stringify({
            timestamp: Date.now(),
            message: "lwt"
        }));
    }
}
exports.send_lwt_msg = send_lwt_msg;

function send_keepalive_msg() {
    if (mqttConnected) {
        client.publish(mqttTopic + topic_status, JSON.stringify({
            timestamp: Date.now(),
            message: "alive"
        }));
    }
}
exports.send_keepalive_msg = send_keepalive_msg;

function send_kpi_results(name, value) {
    if (mqttConnected) {
        client.publish(mqttTopic + util.format(topic_kpi, name), value);
    }
}
exports.send_kpi_results = send_kpi_results;