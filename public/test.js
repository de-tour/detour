var currentWord = "";

function wsReady(ws) {
    function sendRequest(keyword) {
        ws.send(strSuggest(keyword));
    }

    function timer() {

        var word = document.querySelector('#searchbox').value;
        if (word != currentWord) {
            currentWord = word;
            console.log(currentWord);
            sendRequest(word);
        }

        setTimeout(timer, 500);
    }

    timer();

}

$(document).ready(function() {
    function openHandler(event) {
        wsReady(ws);
    }

    function genCard(result){
        var li = document.createElement('li');

        var card = document.createElement('div');
        card.className += " card";

        var card_body = document.createElement('div');
        card_body.className += " card-body";


        var thumb = document.createElement('img');
        thumb.className += " card-thumb";
        if(result['thumbnail'] != null) {
            thumb.src = result['thumbnail'];
        } else {
            thumb.src = '/public/images/detour.png';
        }
        var card_title = document.createElement('h4');
        card_title.className += " card-title";

        var card_subtitle = document.createElement('h6');
        card_subtitle.className += " card-subtitle mb-2 text-muted";
        card_subtitle.textContent = result['source'];

        var card_text = document.createElement('p');
        card_text.className += " card-text";
        card.textContent = result['desc'];

        var card_link = document.createElement('a');
        card_link.className += " card-link";
        card_link.href = result['url'];
        card_link.textContent = result['title'];
        card_title.appendChild(card_link)

        content = [card_title, card_subtitle, thumb, card_text];

        for(i in content) {
            card_body.append(content[i]);
        }

        card_body.appendChild(thumb);
        card.appendChild(card_body);
        card.className += " col-sm";
        return card;
    }

    // Listen for messages
    function msgHandler(event) {
        data = JSON.parse(event.data);
        console.log(data);

        //For suggestions
        if (document.querySelector('#searchbox').value.startsWith(data['from'])) {
            var sugg = document.querySelector('#suggestion');
            sugg.innerHTML = '';

            for (var result of data['results']) {
                var div = document.createElement('div');
                div.innerText = result;
                div.className = "autocomplete"
                sugg.appendChild(div);
            }
        }

        //For search results
        if (data.hasOwnProperty('from_id')) {
            resultsList = document.getElementById('results');
            var idx = 0;
            var cont = document.getElementById("container");
            var row = document.createElement('div');

            for (var result of data['results']) {
                if(idx % 3 == 0){
                    cont.appendChild(row);
                    row = document.createElement('div');
                    row.className = "row";
                }
                row.appendChild(genCard(result));
                idx++;  
            }
        }

    }

    $("autocomplete").click(function(event){
        var query = strSearch($("#searchbox").val(), 0)
        ws.send(query);
    });


    // Connection opened
    var ws = makeWs(openHandler, msgHandler);


    $("#searchbox").keyup(function (event){
        var text = document.querySelector("#searchbox").value;
        // var query = strSuggest($("#searchbox").val())
        // ws.send(query);
        currentWord = text;
    });

    //Submissions

    $("#searchbox").keypress(function (event){
        if(event.keyCode == 13){
            var query = strSearch($("#searchbox").val(), 0)
            ws.send(query);
        }
    });

    $("#submit").click(function (event){
        var query = strSearch($("#searchbox").val(), 0)
        ws.send(query);
    });

    $(document).click(".autocomplete", function (event){
        ws.send(strSearch($(event.target).text(),0));
    });

    // var ws = new WebSocket("ws://" + location.host + "/ws");


});
