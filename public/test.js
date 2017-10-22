$(document).ready(function(){var ws = new WebSocket("ws://" + location.host + "/ws");
    function submit_entry(event){
        console.log("god is dead");
    }

    $("#submit").click(function (event){
        var keyword = encodeURIComponent($("search").val());
        var query = {'verb': 'search', "keyword": keyword};
        ws.send(query);
    })

    // Connection opened
    ws.addEventListener('open', function (event) {
        ws.send('good day!');
    });

    // Listen for messages
    ws.addEventListener('message', function (event) {
        console.log('Message from server ', event.data);
    });
});
