$(document).ready(function(){var ws = new WebSocket("ws://" + location.host + "/ws");
    function submit_entry(event){
        console.log("god is dead");
    }

    $("#submit").click(function (event){
        var query = strSearch($("#search").val(), 0)
        ws.send(query);
    })

    $("#searchbox").keyup(function (event){
        console.log(document.querySelector("#searchbox").value);
        var query = strSuggest($("#searchbox").val())
        ws.send(query);
    })


    function openHandler(event) {
        // Connection opened
            ws.send('👳🏻');
    }

    // Listen for messages
    function msgHandler(event){
        console.log(JSON.parse(event.data).results);
        var div = document.createElement('div');
        div.innerText = JSON.parse(event.data).results;
        document.querySelector('#suggestion').appendChild(div);
    }

    // Connection opened
    var ws = makeWs(openHandler, msgHandler);

});
