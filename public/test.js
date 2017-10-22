var currentWord = "";

function wsReady(ws) {


    function sendRequest(keyword) {
        ws.send(strSuggest(keyword));
    }

    function timer() {
        var word = document.querySelector('#searchbox').value;
        if (word != currentWord) {
            currentWord = word;
            sendRequest(word);
        }

        setTimeout(timer, 500);
    }

    timer();

    $("#submit").click(function (event){
        var query = strSearch($("#search").val(), 0)
        ws.send(query);
    });

    $(".suggestion").click(function (){
        console.log(this.text);
        var query = strSearch($(this).val(), 0)
        ws.send(query);
    })

    $("#searchbox").keyup(function (event){
        var text = document.querySelector("#searchbox").value;
        console.log(text);
        // var query = strSuggest($("#searchbox").val())
        // ws.send(query);
        currentWord = text;
    });


}


$(document).ready(function() {
    function openHandler(event) {
        wsReady(ws);
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


    // var ws = new WebSocket("ws://" + location.host + "/ws");


});
