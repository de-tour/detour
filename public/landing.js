var currentWord = '';

function wsReady(ws) {
    function sendRequest(keyword) {
        ws.send(strSuggest(keyword));
    }

    function timer() {
        var word = document.querySelector('#search-box').value;
        if (word != currentWord) {
            currentWord = word;
            console.log(currentWord);
            sendRequest(word);
        }

        setTimeout(timer, 500);
    }

    timer();

}

function genCard(result) {
    var li = document.createElement('li');

    var card = document.createElement('div');
    card.className += " card";

    var card_body = document.createElement('div');
    card_body.className += " card-body";

    // var thumb = document.createElement('img');
    // thumb.className += " card-thumb";
    // if(result['thumbnail'] != null) {
    //     thumb.src = result['thumbnail'];
    // } else {
    //     thumb.src = '/public/images/detour.png';
    // }

    var thumb = null;
    if (result['thumbnail'] != null) {
        thumb = document.createElement('img');
        thumb.className += " card-thumb";
        thumb.src = result['thumbnail'];
    }

    var card_title = document.createElement('h4');
    card_title.className += " card-title";

    var card_subtitle = document.createElement('h6');
    card_subtitle.className += " card-subtitle mb-2 text-muted";
    card_subtitle.textContent = result['source'];

    var card_text = document.createElement('p');
    card_text.className += " card-text";
    card_text.textContent = result['desc'];

    var card_link = document.createElement('a');
    card_link.className += " card-link";
    card_link.href = result['url'];
    card_link.textContent = result['title'];
    card_title.appendChild(card_link);

    content = [card_title, card_subtitle, card_text, thumb];

    for(var el of content) {
        if (el != null) {
            card_body.appendChild(el);
        }
    }

    // card_body.appendChild(thumb);
    card.appendChild(card_body);
    card.className += " col-sm";
    return card;
}


function main() {
    function clearSuggests() {
        var sugg = document.querySelector('#suggestion');
        sugg.innerHTML = '';
        return sugg;
    }

    function clearResults() {
        var results = document.querySelector('#container');
        // results.innerHTML = '';
        return results;
    }

    function openHandler(event) {
        wsReady(ws);
    }

    // Listen for messages
    function msgHandler(event) {
        var data = JSON.parse(event.data);
        console.log(data);

        // For suggestions
        if (data.hasOwnProperty('from')) {
            var searchBox = document.querySelector('#search-box');
            if (searchBox.value.startsWith(data['from'])) {
                var sugg = clearSuggests();
                for (var result of data['results']) {
                    var div = document.createElement('div');
                    div.innerText = result;
                    div.className = 'autocomplete';
                    div.onclick = function (event) {
                        searchBox.value = div.textContent;
                        submitQuery(div.textContent);
                    }
                    sugg.appendChild(div);
                }
            }
        }

        // For search results
        else if (data.hasOwnProperty('from_id')) {
            var index = 0;
            var container = clearResults();
            var row = document.createElement('div');

            for (var result of data['results']) {
                if(index % 3 == 0) {
                    container.appendChild(row);
                    row = document.createElement('div');
                    row.className = "row";
                }
                row.appendChild(genCard(result));
                index++;
            }
            clearSuggests();
        }
    }

    // Connection opened
    var ws = makeWs(openHandler, msgHandler);

    // Suggestions and Submissions
    function submitQuery(text = null) {
        if (text == null) {
            text = document.querySelector('#search-box').value;
        }
        var query = strSearch(text, 0);
        ws.send(query);
        console.log('Query:', text);
    }

    document.querySelector('#search-button').onclick = function (event) {
        submitQuery();
    };

    document.querySelector("#search-box").onkeypress = function (event) {
        currentWord = document.querySelector("#search-box").value;
        if (event.keyCode == 13) {
            submitQuery();
        }
    };

}

document.addEventListener("DOMContentLoaded", main);
