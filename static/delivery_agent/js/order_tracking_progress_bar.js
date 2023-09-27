$(document).ready(function () {

    var currentstep, nextstep;
    var opacity;
    var current = delivery_status_no;
    var orderId = order_id;
    var steps = $("fieldset").length;

    setProgressBar(current);

    function increaseProgressBar(parent_obj) {
        currentstep = $(parent_obj).parent();
        nextstep = $(parent_obj).parent().next();

        $("#progressbar li").eq($("fieldset")
            .index(nextstep)).addClass("active");

        nextstep.show();
        currentstep.animate({opacity: 0}, {
            step: function (now) {
                opacity = 1 - now;

                currentstep.css({
                    'display': 'none', 'position': 'relative'
                });
                nextstep.css({'opacity': opacity});
            }, duration: 500
        });
        setProgressBar(current);
    }

    const current_ = current

    for (let i = 0; i < current_; i++) {
        increaseProgressBar($('.next-step')[i])
    }

    $('.resend-otp').click(function () {
        let csrftoken = getCookie('csrftoken')
        $.ajax({
            headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
            method: "POST",
            url: "/delivery-agent/resend_otp/",
            data: JSON.stringify({'order_id': orderId}),
            success: function (data) {
                alert('Otp sent!')
            },
            error: function (textStatus, errorThrown) {
                // alert(textStatus.responseJSON);
                alert('OTP not Sent !!')
            }
        })

    });

    $(".next-step").click(function () {
        let csrftoken = getCookie('csrftoken')

        if (current === 2) {

            let otp = prompt('Enter OTP: ');
            $.ajax({
                headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
                method: "POST",
                url: "/delivery-agent/validate_otp/",
                data: JSON.stringify({'otp': otp, 'order_id': orderId}),
                success: function (data) {
                    window.location.reload();
                },
                error: function (textStatus, errorThrown) {
                    alert(
                        "OTP not provided !!"
                    );
                }
            })

        } else {
            ++current;
            increaseProgressBar(this);
            $.ajax({
                headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
                method: "POST",
                url: "/delivery-agent/update_delivery_status/",
                data: JSON.stringify({'id': orderId, 'status': current}),
                success: function (data) {
                    Success = true;
                },
                error: function (textStatus, errorThrown) {
                    Success = false;
                }
            })
        }

    });

    function setProgressBar(currentStep) {
        var percent = parseFloat(100 / steps) * currentStep;
        percent = percent.toFixed();
        $(".form-progress-bar")
            .css("width", percent + "%")
    }

    $(".submit").click(function () {
        return false;
    })
});
