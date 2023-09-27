const restaurant = JSON.parse(document.getElementById('restaurant').textContent);

function connect() {
    chatSocket = new WebSocket("ws://" + window.location.host + "/ws/" + restaurant + "/");

    chatSocket.onopen = function (e) {
        console.log("Successfully connected to the WebSocket.");
    };

    chatSocket.onclose = function (e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function () {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onerror = function (err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    };

    chatSocket.onmessage = function (e) {
        // console.log("new order created.");
        // console.log(e.data)
        const data = JSON.parse(e.data);
        // console.log(data);
        let table_row = " <tr>\n" +
            // "<td>" + data.order + "</td>\n" +
            "<td>\n" +
            "<img alt=\"...\" src=\""+data.profile+"\" class=\"avatar avatar-sm rounded-circle me-2\">\n" +
            "<a class=\"text-heading font-semibold\" href=\"#\">\n" + data.name +
            "</a>\n" +
            "</td>\n" +
            "<td>" + data.date + "</td>\n" +
            "<td>" + data.total + "</td>\n" +
            "<td>" + data.status + "</td>\n" +
            "<td><a href='/restaurant/detail_order/" + data.order +  "/' class=\"btn btn-sm btn-neutral\">View</a></td>\n" +
            "</tr> "
        new_order = $('#orders_received').prepend($(table_row));
    };
}

connect();