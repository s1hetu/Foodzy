$(document).ready(function () {
    $(document.body).on('click', '.accept', function () {
        let data = {"order_id": $(this).data('order')};
        let obj = JSON.stringify(data);
        let csrftoken = getCookie('csrftoken');
        console.log('>>>>>>>>>')
        $.ajax({
            headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
            type: 'POST',
            url: '/delivery-agent/accept_delivery/',
            data: obj,
            success: function (response) {
                console.log(response, '??????????????????')
                $('#myElem').fadeIn('slow');
                $("#myElem").show();
                $('#myElem').delay(5000).fadeOut('slow');

            },
            error: function (response) {
                $('#myElem2').fadeIn('slow');
                $("#myElem2").show();
                $('#myElem2').delay(5000).fadeOut('slow');
            }
        })
    });
})
