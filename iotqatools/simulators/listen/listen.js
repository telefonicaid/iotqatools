/*
Copyright 2015 Telefonica Investigaci�n y Desarrollo, S.A.U

This file is part of telefonica-iotqatools

iotqatools is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

iotqatools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with iotqatools.
If not, seehttp://www.gnu.org/licenses/.

For those usages not covered by the GNU Affero General Public License
please contact with::[iot_support@tid.es]
 */


// requirements
var dateFormat = require('dateformat');
var moment = require('moment');
var mqtt = require('mqtt');

//verbosity flag
var vm=false;

//silence flag
var silence=false;

//timestamp flag
// expected input to calculate the diff in format 2015-10-28T13:51:32+0100
/* {
    "subscriptionId": "56309dbebc0ae94ca4f7f8ea",
    "data": [
      {
        "id": "aaa",
	"type": "xxx",
	"TimeInstant": {
	  "value": "2015-10-28T13:51:32+0100",
	  "type": "ISO8601"
	}
      }
    ]
} */
var timestamp=false;


//accumulator flag
var accumulatorMode=false;

// Simple server for Orion contexBroker notifications:
var http = require('http');

//amount of servers to launch
var servers=3;

//Ports to listen
var port=[1028,1029,1030];

//amount of servers with delay to launch
var delayedServers=1;

//forced delayed response port
var delayedPort=[1031];

//accumulator per second setup
var requests = 0;

//accumulator per session setup
var session_requests = 0;

// show requests every X ms
var samples = 1000;

// delayed response
var delayedtime=2000;

// mqttBroker (if -m is used)
var mqttBroker='';

//Standar CLI options
process.argv.forEach(function (val, index, array) {
        //console.log(index + ': ' + val);
        if (val=="--version"){
                console.log("# Accumulator server version: " + version );
                process.exit(0);
        }
        if (val=="-u" || val=="--help" ){
                console.log("Usage info: \n " +
                                "Accumulator server \n" +
                                " Default configuration launch 3 servers on ports 1028,1029,1030 and 1 server on port 1031 with delayed response of 2 seconds. \n \n" +
                                "for modify the configuration use: > noode nodeAccumulator.js [-u -v --version --silence -s -p -ds -dp] \n" +
                                " \n - Params \n" +
                                " '-u' : Shows this usage info \n" +
                                " '--help' : Shows this usage info \n" +
                                " '-sX' : amount of servers to run (without delay). '-d5' will launch 5 servers \n"+
                                " '-pX' : Port Server, X is the first port number to setup the server, the rest of listener servers will be added in the next port numbers \n"+
                                " '-dsY' : amount of delayed servers tu run with delay. '-ds3' will launch 3 servers  \n"+
                                " '-dpY' : Port Delayed Server, Y is the first port number to setup the Delayed server, the rest of listener servers will be added in the next port numbers \n"+
                                " '--silence' : no info showed in log \n" +
                                " '--version' : shows the version of this script \n" +
                                " '-v' : verbose mode, by default OFF \n" +
                                " '-t' : timestamp diff mode, by default OFF \n" +
                                " '-a' : accumulator mode, by default OFF \n" +
                                " '-mX' : MQTT mode for broker at X (e.g. -mlocalhost:1883)\n");
                process.exit(0);
        }
        if (val=="-v"){
                console.log("# Verbosity Activated");
                vm=true;
        }
        if (val=="-t"){
                console.log("# Timestamp Activated");
                timestamp=true;
        }
        if (val=="-a"){
                console.log("# AccumulatorMode Activated");
                accumulatorMode=true;
        }
        if (val=="--silence"){
                silence=true;
        }
        if (val.match(/^-s/)) {
                servers=val.slice(2);
        }
        if (val.match(/^-m/)) {
                mqttBroker=val.slice(2);
        }
        if (val.match(/^-ds/)) {
                delayedServers=val.slice(3);
        }
        if (val.match(/^-p/)) {
                console.log("Setup ports starting at : ",val.slice(2));
                for (var i=0; i<servers; i++){
                        port[i]=val.slice(2);
                        port[i]=eval(port[i])+i;
                }
        }
        if (val.match(/^-dp/)) {
                console.log("Setup Delayed ports starting at : ",val.slice(3));
                for (var i=0; i<delayedServers; i++){
                        delayedPort[i]=val.slice(3);
                        delayedPort[i]=eval(delayedPort[i])+i;
                }
        }

});

var processData = function(data) {
        if(timestamp) {
                //console.log('# Notification Data: ' + data);
                // get current time
                var now = new Date();
                //var current = dateFormat(now, "isoDateTime");
                var current = dateFormat(now, "yyyy-mm-dd'T'HH:MM:ssl");

                try {
                        var context = JSON.parse(data);

                        // get Data from update
                        var received = context.data[0].TimeInstant.value;
                        //var time = dateFormat(received, "isoDateTime");
                        var time = dateFormat(received, "yyyy-mm-dd'T'HH:MM:ssl");
                        console.log("# TimeInstant  NOW: "+ current + " RECEIVED: " + time);

                        //calculate DIFF
                        //var startDate = moment(time);
                        //var endDate = moment(current);
                        var startDate = moment(received);
                        var endDate = moment(now);
                        //var secondsDiff = endDate.diff(startDate, 'seconds');
                        var secondsDiff = endDate.diff(startDate);
                        console.log("# Diff: "+ secondsDiff);
                                    
                }
                catch (e) {
                        return console.error(e);
                }

                                
        }
        if (vm) {
                console.log('# Notification Data: ' + data);
        }
}

// Create an HTTP server
var srv =function(){
        return http.createServer(function(req, res) {
                'use strict';
                requests++;

                req.on('data', processData);
                req.on('end', function() {
                        setTimeout(function() {
                                res.writeHead(200, {'Content-Type': 'text/plain'});
                                res.end('OK \n');
                        });
                });
        })
};

var delaySrv = function(){
        return http.createServer(function(req, res) {
                'use strict';
                requests++;

                req.on('data', function(data) {
                        if(vm){
                                console.log('# Notification Delayed server: ' + data);
                        }
                });
                req.on('end', function() {
                        setTimeout(function() {
                                res.writeHead(200, {'Content-Type': 'text/plain'});
                                res.end('OK delayed \n');
                        }, delayedtime);
                });
        })
};

// HTTP servers started only if MQTT mode is not being used
if (mqttBroker == '') {
        // start servers
        for (var i=0; i<servers; i++){
                srv().listen(port[i]);
                if (!silence){
                        console.log("### ACCUMULATOR SERVER  #"+ eval(i+1) +" STARTED at port " + port[i] +" ###", Date());}
        };
        // start severs with delay
        for (var i=0; i<delayedServers; i++){
                delaySrv().listen(delayedPort[i]);
                if(!silence){
                        console.log("### ACCUMULATOR Delayed SERVER #"+ eval(i+1) +" + STARTED at port " + delayedPort[i] +" ###", Date());}
        };
}
else {
        var client  = mqtt.connect("mqtt://" + mqttBroker);
        client.on("connect", function(){
                console.log("connected");
        })

	// Just # is too broad, maybe use /orion as prefix
        client.subscribe('/orion/#');

        client.on('message', function(topic, message, packet){
                //console.log("message is "+ message);
                //console.log("topic is "+ topic);
                requests++;
                processData(message);
        });
}

setInterval(function () {
        if(!silence){
                if (accumulatorMode){
                        console.log('Req: ' + requests + ' [' + session_requests + ']');
                }
                else{
                        console.log('Req: ' + requests);
                }
        }
        if (requests != 0) {
                if (accumulatorMode){
                        session_requests += requests;
                }
                requests = 0;
        }
        
}, samples);
