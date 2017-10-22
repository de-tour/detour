function strSuggest(keyword) {
    return JSON.stringify({'verb': 'suggest', 'keyword': encodeURIComponent(keyword)});
}

function strSearch(keyword, fromId) {
    return JSON.stringify({'verb': 'search', 'keyword': encodeURIComponent(keyword), 'from_id': fromId});
}

function makeWs(openHandler, msgHandler) {
    var ws = new WebSocket("ws://" + location.host + "/ws");

    // Connection opened
    ws.addEventListener('open', openHandler);

    // Listen for messages
    ws.addEventListener('message', msgHandler);

    return ws;
}
