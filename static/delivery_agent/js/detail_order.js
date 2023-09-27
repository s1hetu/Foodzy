$('input.status').change(
    function () {
        if (this.checked) {
            let status = {"status": $(this).val()};
            let obj = JSON.stringify(status)
            let csrftoken = getCookie('csrftoken');

            $.ajax({

                headers: {'X-CSRFToken': csrftoken, 'Content-Type': 'application/json'},
                type: 'POST',
                data: obj,
                success: function (response) {
                    window.location.reload();
                },
                error: function (response) {
                    alert(response["responseJSON"]["error"]);
                }
            })
        }
    });
