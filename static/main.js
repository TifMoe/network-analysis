    //Javascript to create a D3js force graph visualization

    //create somewhere to put the force directed graph
    var svg = d3.select("svg"),
     width = +svg.attr("width"),
     height = +svg.attr("height");

    var radius = 15;

    //add encompassing group for the zoom
    var g = svg.append("g")
        .attr("class", "everything");

    //add zoom capabilities
    var zoom_handler = d3.zoom()
        .on("zoom", zoom_actions);

    zoom_handler(svg);

    function zoom_actions(){
        g.attr("transform", d3.event.transform)
    }


    //d3 code goes here
    d3.json("/data", function(error, graph) {

        //Entities
        var nodes_data = graph.nodes;

        //Relationships
        var links_data = graph.edges;

        //set up the simulation
        //nodes only for now
        var simulation = d3.forceSimulation()
            .nodes(nodes_data);

        var forceCollide = d3.forceCollide()
            .radius(function(d){return d.radius;})
            .iterations(2)
            .strength(0.95);

        //add forces
        //we're going to add a charge to each node
        //also going to add a centering force
        simulation
            .force("charge_force", d3.forceManyBody().strength(-2))
            .force("center_force", d3.forceCenter(width / 2, height / 2))
            .force("collide", forceCollide);


        var tooltip = d3.select("body")
            .append("g")
            .style("position", "absolute")
            .style("z-index", "10")
            .style("visibility", "hidden")
            .text('no info');

        //draw lines for the links
        var link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links_data)
            .enter().append("line")
            .attr("stroke-width", 1)
            .style('stroke', 'grey');


        //draw circles for the nodes
        var node = g.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(nodes_data)
            .enter()
            .append("circle")
            .attr("r", circleSize)
            .attr("fill", circleColour)
            .on("click", function(d){
                console.log(d.id)})
            .on("mouseover", function(d){return tooltip.style("visibility", "visible").text(d.id);})
            .on("mousemove", function(){return tooltip.style("top",
                (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");})
            .on("mouseout", function(){return tooltip.style("visibility", "hidden");});


        //Function to choose what color circle we have
        //Let's return blue for males and red for females
        function circleColour(d){
            if(d.type == "provider"){
                return "#cd6200";
            } else if(d.type == "phone_number"){
                return "#cdc900";
            } else {
                return "#5e6e62";
            }
        }

        function circleSize(d){
            if(d.type == 'provider'){
                return 18;
            } else {
                return 7;
            }
        }


        //Create the link force
        //We need the id accessor to use named sources and targets
        var link_force = d3.forceLink(links_data)
            .id(function (d) {
                return d.id;
            })

        function box_force() {
          for (var i = 0, n = nodes_data.length; i < n; ++i) {
            curr_node = nodes_data[i];
            curr_node.x = Math.max(radius, Math.min(width - radius, curr_node.x));
            curr_node.y = Math.max(radius, Math.min(height - radius, curr_node.y));
          }
        }

        simulation
            .force("links", link_force)
            .force("box_force", box_force);


        function tickActions() {
            //update circle positions each tick of the simulation
            node
                .attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });

            //update link positions
            //simply tells one end of the line to follow one node around
            //and the other end of the line to follow the other node around
            link
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

        }

        simulation.on("tick", tickActions);


        var drag_handler = d3.drag()
            .on("start", drag_start)
            .on("drag", drag_drag)
            .on("end", drag_end);


        function drag_start(d) {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function drag_drag(d) {
            d.fx = Math.max(radius, Math.min(width - radius, d3.event.x));
            d.fy = Math.max(radius, Math.min(height - radius, d3.event.y));
        }

        function drag_end(d) {
            if (!d3.event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        drag_handler(node)
    });

