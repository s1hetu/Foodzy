$(document).ready(function () {
    $(document.body).on('click', '.received', function () {
        let data = {"order_id": $(this).data('order')};
        let obj = JSON.stringify(data);
        let csrftoken = getCookie('csrftoken');


        $.ajax({
            headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
            type: 'POST',
            url: '/delivery-agent/accept_payment/',
            data: obj,
            success: function (response) {
                window.location.reload();
            },
            error: function (response) {
                $("#paymentStatus2").fadeIn('slow');
                $("#paymentStatus2").addClass('box-element');
                $("#paymentStatus2 div").css('display', 'block');
                $("#paymentStatus2").delay(4000).fadeOut('slow');


            }
        })
    });
})
