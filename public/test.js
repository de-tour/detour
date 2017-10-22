var ws = new WebSocket("ws://" + location.host + "/ws");
$("#tit")
function submit(event){
    return event.name;
}
// ws.send("wtf am I doing?")


// Connection opened
ws.addEventListener('open', function (event) {
    ws.send('Hello Server! WTF am I doing?');
});

// Listen for messages
ws.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
});
