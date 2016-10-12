// - get command line arguments
var argv = require('minimist')(process.argv.slice(2));
var redis_host = argv['redis_host']
var redis_port = argv['redis_port']
var subscribe_channel = argv['channel']


// -setup dependency instance
// backbone, amber other framwork like express
var express = require('express');
var app = express();
var server = require('http').createServer(app)
var io =require('socket.io')(server)

var redis = require('redis')
console.log('Creating redis client')
var redisclient = redis.createClient(redis_port,redis_host)
console.log('Subsribe to redis topic %s', subscribe_channel)
redisclient.subscribe(subscribe_channel)
redisclient.on('message', function(channel, message){
	if (channel == subscribe_channel){
		console.log('message received %s', message)
		io.sockets.emit('data',message)
	}
})

// - setup webapp routing
app.use(express.static(__dirname + '/public'));

// - grab information from backend to frontend
app.use('/jquery',express.static(__dirname + '/node_modules/jquery/dist/'));
app.use('/smoothie', express.static(__dirname + '/node_modules/smoothie/'));

server.listen(3000, function (){
	console.log('Server started at 3000')
})

// - setup shutdown hook
var shutdown_hook = function(){
	console.log('Quitting redis client')
	redisclient.quit()
	console.log('Shutting down app')
	process.exit();
}

// process.on('SIGTERM', shutdown_hook)
// process.on('SIGINT', shutdown_hook)
// process.on('exit', shutdown_hook)