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
        console.log(JSON.parse(event.data).results);
        var div = document.createElement('div');
        div.innerText = JSON.parse(event.data).results;
        document.querySelector('#suggestion').appendChild(div);
    }
    // Connection opened
    var ws = makeWs(openHandler, msgHandler);


    // var ws = new WebSocket("ws://" + location.host + "/ws");


});
