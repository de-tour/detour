$(document).ready(function(){var ws = new WebSocket("ws://" + location.host + "/ws");
    function submit_entry(event){
        console.log("god is dead");
    }

    $("#submit").click(function (event){
        var query = strSearch($("#search").val(), 0)
        ws.send(query);
    })

    $(".suggestion").click(function (){
        console.log(this.text);
        var query = strSearch($(this).val(), 0)
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
        var data = JSON.parse(event.data);
        var text_value =  document.getElementById('searchbox').value;
        console.log(data, text_value);

        if(text_value.startsWith(data['from'])) {

            $("#suggestions").html("");
            for(suggestion of data['results']){
                var sugg = document.createElement('tr');
                sugg.innerText = suggestion;
                sugg.class = "suggestion";
                $('#suggestions').append(sugg);
            }
        }
    }
    // Connection opened
    var ws = makeWs(openHandler, msgHandler);

});
