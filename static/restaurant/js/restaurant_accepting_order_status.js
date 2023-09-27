$(document).ready(function () {
    $('#toggle-two').bootstrapToggle($('#toggle-two').val());

    let alert = `<div class="alert alert-danger alert-dismissible fade show" 
                                 style="display:none">
                                You have some orders to prepare.
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>`;

    $(function () {
        $('#toggle-two').change(function () {
            if ($(this).val() === true) {
                $(this).val(false)
            } else {
                $(this).val(false)
            }
            let csrftoken = getCookie('csrftoken')
            let restaurant_status = $(this).prop('checked');
            $.ajax({
                headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
                method: "POST",
                url: "/restaurant/restaurant_status/" + restaurant + "/",
                // url: "{% url 'restaurant-status' restaurant %}",
                data: JSON.stringify({'status': restaurant_status}),
                success: function (data) {
                },
                error: function (textStatus, errorThrown) {
                    $('#myStatus').html(alert);
                    $("#myStatus div").css('display', 'block')
                }
            })

        })

        if (pending_orders === "True") {
            $('#toggle-two').prop('disabled', true);
        }

        $('#toggle-two').parent().on('click', function () {
            if (pending_orders === 'True') {
                $('#myStatus').html(alert);
                $("#myStatus div").css('display', 'block')
            }
        })
    })
})

