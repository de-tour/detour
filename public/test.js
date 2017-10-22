var ws = new WebSocket("ws://" + location.host + "/ws");

function submit_entry(event){
    console.log("god is dead");
    //ws.send($(".tit").value)
}

document.getElementById("submit").click(submitentry)


// Connection opened
ws.addEventListener('open', function (event) {
    ws.send('good day!');
});

// Listen for messages
ws.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
});
