$(document).ready(function(){var ws = new WebSocket("ws://" + location.host + "/ws");
    function submit_entry(event){
        console.log("god is dead");
    }

    $("#submit").click(function (event){
        var query = strSearch($("#search").val(), 0)
        ws.send(query);
    })

    $("#searchbox").keyup(function (event){
        var query = strSearch($("#search").val(), 0)
        ws.send(query);
    })

    // Connection opened
    var ws = makeWs();
});
