function connect() {
    let chatSocket = new WebSocket("ws://" + window.location.host + "/ws/");

    chatSocket.onopen = function (e) {
    };

    chatSocket.onclose = function (e) {
        setTimeout(function () {
            connect();
        }, 2000);
    };

    chatSocket.onerror = function (err) {
        chatSocket.close();
    };

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.type === 'order.received') {
            let table_row = " <tr id = \'row-" + data.order + "\'>\n" +
                "<td>" + data.order + "</td>\n" +
                "<td>\n" +
                "<img alt=\"...\" src=\"" + data.profile + "\" class=\"avatar avatar-sm rounded-circle me-2\">\n" +
                "<a class=\"text-heading font-semibold\" href=\"#\">\n" + data.name +
                "</a>\n" +
                "</td>\n" +
                "<td>" + data.date + "</td>\n" +
                "<td>" + data.total + "</td>\n" +
                "<td style=\"text-align: center\"><button class=\"accept\" data-order=\'" + data.order + "\'>ACCEPT<span class=\"fa fa-check\"></span></button></td>" +
                "<td><a href='/delivery_agent/detail_delivery/" + data.order + "/' class=\"btn btn-sm btn-neutral\">View</a></td>\n" +
                "</tr>"
            $('#orders_received').append($(table_row));
        }
        if (data.type === 'delivery.accepted') {
            $('#row-' + data.id).remove()
            if ($('#orders_received').children().length === 0) {
                window.location.reload();
            }
        }
    };
}

connect();

