$(function(){
    $("#provider").hide();
});


    //Javascript to create a D3js force graph visualization

    //create somewhere to put the force directed graph
    var svg = d3.select("svg"),
     width = +svg.attr("width"),
     height = +svg.attr("height");

    var radius = 15;

    //add encompassing group for the zoom
    var g = svg.append("g")
        .attr("class", "everything");


    //d3 code goes here
    d3.json("/data", function(error, graph) {

        //Entities
        var nodes_data = graph.nodes;

        //Relationships
        var links_data = graph.edges;

        //set up the simulation
        const forceX = d3.forceX(width / 2).strength(0.015)
        const forceY = d3.forceY(height / 2).strength(0.015)

        var simulation = d3.forceSimulation()
            .nodes(nodes_data)
            .force('x', forceX)
            .force('y', forceY);


        var forceCollide = d3.forceCollide()
            .radius(function(d){return d.radius;})
            .iterations(2)
            .strength(1);

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
            .on("mouseover", ToolTipOver)
            .on("mousemove", ToolTipMove)
            .on("mouseout", ToolTipOut);

        var label = svg.selectAll(null)
            .data(graph.nodes)
            .enter()
            .append("text")
            .text(function (d) { if(d.type == "provider"){ return d.dense_rank; }})
            .style("text-anchor", "middle")
            .style("fill", "#fff")
            .style("font-family", "Arial")
            .style("font-size", 15)
            .on("mouseover", ToolTipOver)
            .on("mousemove", ToolTipMove)
            .on("mouseout", ToolTipOut);


        function ToolTipOver(d){
            if (d.type != 'reviewer'){
            return tooltip
                .style("visibility", "visible").text(d.name)
                .style("cursor", "pointer");
            }
        }

        function ToolTipMove(d){
            if (d.type != 'reviewer'){
                return tooltip
                    .style("top", (d3.event.pageY-10)+"px")
                    .style("left",(d3.event.pageX+10)+"px")
                    .style("cursor", "pointer");;
            }
        }

        function ToolTipOut(d){
            if (d.type != 'reviewer'){
                return tooltip.style("visibility", "hidden");
            }
        }


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
                return 25;
            } else if(d.type == 'phone_number') {
                return 12;
            } else {
                return 8;
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

            label.attr("x", function(d){ return d.x; })
    			 .attr("y", function (d) {return d.y + 3; });

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
        drag_handler(label)

        /*Create Priority List Div */

        var provider_nodes = $.grep(graph.nodes, function (element, index) {
            return element.type == 'provider';
        });

        $.each(provider_nodes, function () {

            var newProvider = $("body").find("#provider > div").clone();

            newProvider.find(".name").append(this.name);
            newProvider.find(".phone").append(this.attributes['Phone Number']);
            newProvider.find(".date").append(this.max_date);
            newProvider.find(".rank").append(this.dense_rank);
            newProvider.find(".status").append(this.status);

            $(newProvider).appendTo(".node_list");
          });

});

