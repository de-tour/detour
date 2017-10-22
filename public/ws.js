function strSuggest(keyword) {
    return JSON.stringify({'verb': 'suggest', 'keyword': encodeURIComponent(keyword)});
}

function strSearch(keyword, fromId) {
    return JSON.stringify({'verb': 'search', 'keyword': encodeURIComponent(keyword), 'from_id': fromId});
}

function makeWs() {
    var ws = new WebSocket("ws://" + location.host + "/ws");

    // Connection opened
    ws.addEventListener('open', function (event) {
        ws.send('good day');
    });

    // Listen for messages
    ws.addEventListener('message', function (event) {
        console.log('Message from server ', event.data);
    });

    return ws;
}
