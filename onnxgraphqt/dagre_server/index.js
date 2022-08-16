var http = require('http');
var url = require('url');
var view = view || require('./view');
var dagre = dagre || require('./dagre');

// Server
const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
    console.log('request : ' + req.url);
    var url_parse = url.parse(req.url, true);
    var path_name = url_parse.pathname;
    var chunks = "";
    if (path_name === "/layout"){
        if(req.method === "POST"){
            req.on("data", function(chunk){
                chunks += chunk;
            }).on("end", function(){
                var graph_data = JSON.parse(chunks.toString());
                // Graph Option
                const options = {};
                options.nodesep = 20;
                options.ranksep = 20;
                // Create Graph
                const viewGraph = new view.Graph(undefined, undefined, undefined, options);
                try{
                    viewGraph.add(graph_data);
                    viewGraph.build(req.document, undefined);
                    viewGraph.options = options
                    viewGraph._nodes.forEach(function(v) {
                        v.label.width = 1;
                        v.label.height = 1;
                    });

                    dagre.layout(viewGraph);
                }catch(err){
                    console.log(err);
                    res.statusCode = 400;
                    res.end('400 Bad Request.' + err);
                    return;
                }

                var response = {};
                response["inputs"] = {};
                response["nodes"] = {};
                response["outputs"] = {};

                viewGraph._nodes.forEach(function(v) {
                    var type = v.label.id.split("-")[0];
                    if (type === "input"){
                        response["inputs"][v.label.value.name] = {};
                        response["inputs"][v.label.value.name]["x"] = v.label.x;
                        response["inputs"][v.label.value.name]["y"] = v.label.y;
                    }
                    else if (type === "output"){
                        response["outputs"][v.label.value.name] = {};
                        response["outputs"][v.label.value.name]["x"] = v.label.x;
                        response["outputs"][v.label.value.name]["y"] = v.label.y;
                    }
                    else if (type === "node"){
                        response["nodes"][v.label.value.name] = {};
                        response["nodes"][v.label.value.name]["x"] = v.label.x;
                        response["nodes"][v.label.value.name]["y"] = v.label.y;
                    }
                    console.log(v.label.value.name + ": " + "(" + v.label.x + "," + v.label.y + ")");
                });

                console.log(url_parse.pathname);
                console.log(url_parse.query.data);
                res.statusCode = 200;
                res.setHeader('Content-Type', 'application/json');
                res.end(JSON.stringify(response));
                return;
            })
        };
    }else{
        res.statusCode = 404;
        res.end('404 not found.');
    }
});

server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});
