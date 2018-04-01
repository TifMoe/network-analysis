//Nodes V2

var width = 300,
    height = 300,
    colors = d3.scale.category20b();

var force = d3.layout.force()
    .gravity(.2)
    .charge(-3000)
    .size([width, height]);

//Svg Chart SVG Settings
var svg = d3.select("#chart").append("svg:svg")
    .attr("width", width)
    .attr("height", height);

var root = getData();
var nodes = flatten(root),
    links = d3.layout.tree().links(nodes);

nodes.forEach(function(d, i) {
    d.x = width/2 + i;
    d.y = height/2 + 100 * d.depth;
});

root.fixed = true;
root.x = width / 2;
root.y = height / 2;

force.nodes(nodes)
    .links(links)
    .start();

var link = svg.selectAll("line")
    .data(links)
   .enter()
    .insert("svg:line")
    .attr("class", "link");

var node = svg.selectAll("circle.node")
    .data(nodes)
   .enter()
    .append("svg:circle")
    .attr("r", function(d) { return d.size/200; })
    //.attr('fill', function(d) { return d.color; }) // Use Data colors
    .attr('fill', function(d, i) { return colors(i); }) // Use D3 colors
    .attr("class", "node")
    .call(force.drag)

    .on('click', function(){
        d3.select( function (d){
            return i.li;
        })
            .style('background', '#000')
    })

//Adding an event - mouseover/mouseout
    .on('mouseover', onMouseover)

    .on('mouseout', onMouseout);

//Add a legend
var legend = d3.select('#key').append('div')
    .append('ul')
    .attr('class', 'legend')
    .selectAll('ul')
    .data(nodes)
    .enter().append('li')
        .style('background', '#ffffff')
    .text(function(d) { return d.name; })

    .on('mouseover', onMouseover)

    .on('mouseout', onMouseout)

    .append('svg')
        .attr('width', 10)
        .attr('height', 10)
        .style('float', 'right')
        .style('margin-top', 4)
    .append('circle')
        .attr("r", 5)
        .attr('cx', 5)
        .attr('cy', 5)
        .style('fill', function(d, i) { return colors(i); });

//Add Ticks
force.on("tick", function(e) {

    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

});


//Center Node
var userCenter = d3.select("svg").append("svg:circle")
    .attr('class', 'user')
    .attr('r', 30)
    .attr('cx', width/2)
    .attr('cy', height/2)
    .style('fill', '#bfbfbf')

var label = d3.select('svg').append("text")
    .text('USER')
    .attr('x', width/2)
    .attr('y', height/2)
    .attr('text-anchor','middle')
    .attr('transform', 'translate(0, 5)')
    .style('font-size','12px')
    .attr('fill','#666666')

//Fix Root
function flatten(root) {
    var nodes = [];
    function recurse(node, depth) {
        if (node.children) {
            node.children.forEach(function(child) {
                recurse(child, depth + 1);
            });
        }
        node.depth = depth;
        nodes.push(node);
    }
    recurse(root, 1);
    return nodes;
}

function onMouseover(elemData) {

		d3.select("svg").selectAll("circle")
    .select( function(d) { return d===elemData?this:null;})
    .transition()//Set transition
                .style('stroke', '#222222')
                .attr("r", function(d) { return (d.size/200) + 2; })

     d3.select('#key').selectAll('li')
     .select( function(d) { return d===elemData?this:null;})
            .transition().duration(200)//Set transition
            .style('background', '#ededed')


}

function onMouseout(elemData) {

		d3.select("svg").selectAll("circle")
    .select( function(d) { return d===elemData?this:null;})
								.transition()
                .style('stroke', '#bfbfbf')
                .attr("r", function(d) { return (d.size/200) - 2; })

     d3.select('#key').selectAll('li')
     .select( function(d) { return d===elemData?this:null;})
 						.transition().duration(500)//Set transition
            .style('background', '#ffffff')


}

//Data
function getData() {
    return {
        "name": "flare",
        "size": 0,
            "children": [
                { "name": "Jobs", "size": 3743 },
                { "name": "Contact", "size": 3302 },
                { "name": "Dietary", "size": 2903 },
                { "name": "Bookings", "size": 4823 },
                { "name": "Menu", "size": 3002 },
                { "name": "Cards", "size": 3120 },
                { "name": "Newsletter", "size": 3302 }
            ]
    };
}