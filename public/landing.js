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

        setTimeout(timer, 1000);
    }

    timer();

}

function genCard(result) {
    var li = document.createElement('li');

    var card = document.createElement('div');
    card.className += " card";

    var card_body = document.createElement('div');
    card_body.className += " card-body";

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
    card.appendChild(card_body);
    card.className += " col-sm";
    return card;
}

function redirect(text = null) {
    if (text == null) {
        text = document.querySelector('#search-box').value;
    }
    location.href = '/?q=' + encodeURIComponent(text);
}

function genSugg(text) {
    var div = document.createElement('div');
    div.innerText = text;
    div.className = 'autocomplete';
    div.onclick = function (event) {
        redirect(text);
    }

    return div;
}

function queryParse(query) {
    var queryDict = {}
    var queryTuples = query.substring(1).split('&');
    for (var t of queryTuples) {
        var index = t.indexOf('=');
        if (index >= 0) {
            var key = t.substring(0, index);
            var value = decodeURIComponent(t.substring(index + 1));
            queryDict[key] = value;
        }
    }
    return queryDict;
}


function main() {
    function clearSuggests() {
        var sugg = document.querySelector('#suggestion');
        sugg.innerHTML = '';
        return sugg;
    }

    function containerDiv() {
        return document.querySelector('#container');
    }

    // Suggestions and Submissions
    function submitQuery(text = null) {
        if (text == null) {
            text = document.querySelector('#search-box').value;
        }
        var query = strSearch(text, 0);
        ws.send(query);
        console.log('Query:', text);
    }

    function renderSugg(data) {
        var searchBox = document.querySelector('#search-box');
        if (searchBox.value.startsWith(data['from'])) {
            var sugg = clearSuggests();
            for (var result of data['results']) {
                sugg.appendChild(genSugg(result));
            }
        }
    }

    var nResults = 0;

    function renderResults(data) {
        var index = 0;
        var container = containerDiv();
        var row = document.createElement('div');

        for (var result of data['results']) {
            if (index % 3 == 0) {
                container.appendChild(row);
                row = document.createElement('div');
                row.className = "row";
            }
            row.appendChild(genCard(result));
            index++;
            nResults++;
        }
        clearSuggests();

        document.querySelector('#num-results').innerText = nResults + ' result' + ((nResults > 1 ? 's' : ''));
        document.querySelector('#page-num').innerText = data['from_id'] + 1;
        document.querySelector('#metadata').classList.remove('hidden');
    }

    function openHandler(event) {
        // parse URL
        var queries = queryParse(new URL(location.href).search);
        var keyword = queries['q']
        if (keyword) {
            document.querySelector("#search-box").value = keyword;
            submitQuery(keyword);
        }
        wsReady(ws);
    }

    // Listen for messages
    function msgHandler(event) {
        var data = JSON.parse(event.data);
        console.log(data);

        // For suggestions
        if (data.hasOwnProperty('from')) {
            renderSugg(data);
        }
        // For search results
        else if (data.hasOwnProperty('from_id')) {
            renderResults(data);
        }
    }

    document.querySelector('#search-button').onclick = function (event) {
        redirect();
    };

    document.querySelector("#search-box").onkeypress = function (event) {
        currentWord = document.querySelector("#search-box").value;
        if (event.keyCode == 13) {
            redirect();
        }
    };

    // Connection opened
    var ws = makeWs(openHandler, msgHandler);
}

document.addEventListener("DOMContentLoaded", main);
