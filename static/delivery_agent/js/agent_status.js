$(document).ready(function () {
    let alert1 = `<div class="alert alert-danger alert-dismissible fade show" 
                             style="display:none">
                            You have Some orders to deliver.
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>`;

    if ($("#toggle-two").val() == 'on') {
        $("#toggle-two").parent().removeClass('btn-secondary').addClass('btn-success');
        $("#toggle-two").parent().removeClass('off');
        $("#toggle-two").parent().addClass('on');
        $("#toggle-two").prop('checked', true)
    }

    if (active_delivery === "True") {
        let csrftoken = getCookie('csrftoken');
        $.ajax({
            headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
            method: "POST",
            url: "/delivery-agent/update-status/",
            data: JSON.stringify({'status': 'Available'}),
            success: function (data) {
                Success = true;
                $("#toggle-two").val('on')
                $("#toggle-two").parent().removeClass('btn-secondary').addClass('btn-success');
                $("#toggle-two").parent().removeClass('off');
                $("#toggle-two").parent().addClass('on');
            },
            error: function (textStatus, errorThrown) {
                Success = false;

            }
        });
    }

    $(function () {
        $('#toggle-two').change(function () {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function (position) {
                    if ($("#toggle-two").val() === 'on') {
                        $("#toggle-two").val('off')
                        $("#toggle-two").parent().removeClass('on');
                        $("#toggle-two").parent().addClass('off');
                        $("#toggle-two").prop('checked', false)
                    } else {
                        $("#toggle-two").val('on')
                        $("#toggle-two").parent().removeClass('off');
                        $("#toggle-two").parent().addClass('on');
                        $("#toggle-two").prop('checked', true)
                    }
                    let csrftoken = getCookie('csrftoken')
                    let agent_status = $("#toggle-two").prop('checked');
                    if (agent_status){
                        agent_status = 'Available'
                    }
                    else {
                        agent_status = 'Not Available'
                    }

                    $.ajax({
                        headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
                        method: "POST",
                        url: "/delivery-agent/update-status/",
                        data: JSON.stringify({'status': agent_status}),
                        success: function (data) {
                            Success = true;
                        },
                        error: function (textStatus, errorThrown) {
                            $('#myStatus').html(alert1);
                            $("#myStatus div").css('display', 'block')
                            Success = false;
                        }
                    });
                }, function (positionError) {
                    if ($("#toggle-two").val() == "on") {
                        let csrftoken = getCookie('csrftoken')
                        let alert1 = `<div class="alert alert-danger alert-dismissible fade show" 
                             style="display:none">
                            Please turn on your location!
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>`;

                        $.ajax({
                            headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
                            method: "POST",
                            url: "/delivery-agent/update-status/",
                            data: JSON.stringify({'status': 'Not Available'}),
                            success: function (data) {
                                $('#myStatus').html(`<div class="alert alert-warning alert-dismissible fade show" 
                                                                 style="display:none">
                                                                Please turn on your location!
                                                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                                            </div>`);
                                $("#myStatus div").css('display', 'block')
                                Success = true;
                            },
                            error: function (textStatus, errorThrown) {
                                Success = false;
                            }
                        });
                    } else {
                        $('#myStatus').html(`<div class="alert alert-danger alert-dismissible fade show" 
                                                                 style="display:none">
                                                                Please turn on your location!
                                                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                                            </div>`);
                        $("#myStatus div").css('display', 'block')
                    }
                    $("#toggle-two").parent().removeClass('btn-success').addClass('btn-secondary');
                    $("#toggle-two").parent().removeClass('on');
                    $("#toggle-two").parent().addClass('off');
                    $("#toggle-two").prop('checked', false)
                })
            }
        });


        $('#toggle-two').parent().click(function () {
            if (active_delivery === "True") {
                $('#toggle-two').prop('disabled', true);
                $('#myStatus').html(alert1);
                $("#myStatus div").css('display', 'block')
            }
        });

    });
})