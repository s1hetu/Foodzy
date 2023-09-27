$(document).ready(function () {
    function check_authenticated() {
        if (is_authenticated === 'False') {
            window.location.href = window.location.origin + login_url + '?next=' + window.location.pathname;
        }
    }

    // JavaScript function to get cookie by name; retrieved from https://docs.djangoproject.com/en/3.1/ref/csrf/
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // JavaScript wrapper function to send HTTP requests using Django's "X-CSRFToken" request header
    function sendHttpAsync(path, method, body) {
        check_authenticated();

        let props = {
            method: method, headers: {
                'Accept': 'application/json', 'Content-Type': 'application/json', "X-CSRFToken": getCookie("csrftoken")
            }, mode: "same-origin",
        }

        if (body !== null && body !== undefined) {
            props.body = JSON.stringify(body);
        }
        return fetch(path, props)
            .then(response => {
                console.log(response)
                return response.json().catch(() => null)
                    .then(result => {
                        return {
                            status: response.ok, body: result
                        }
                    });
            })
            .then(resultObj => {
                return resultObj;
            })
            .catch(error => {
                throw error;
            });
    }

    add_to_cart = (item_id) => {
        let requestBody = {
            'item': item_id
        };

        sendHttpAsync("/cart/create-item/", "POST", requestBody)
            .then(response => {
                if (response.status) {
                    const remove_from_cart_button = $('<button>remove from cart</button>')
                        .attr('onClick', 'remove_from_cart(' + item_id + ')')
                        .attr('class', 'btn btn-danger')
                    $("#product-button-" + item_id).html(remove_from_cart_button)
                }
            });
    }

    remove_from_cart = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/delete-item/" + item_id + "/", "POST", requestBody)
            .then(response => {
                if (response.status) {
                    const remove_from_cart_button = $('<button>Add to cart</button>')
                        .attr('onClick', 'add_to_cart(' + item_id + ')')
                        .attr('class', 'btn btn-primary')
                    $("#product-button-" + item_id).html(remove_from_cart_button)
                }
            });
    }

    increase_quantity = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/increase-item-quantity/" + item_id + "/", "POST", requestBody)
            .then(response => {
                $("#quantity-" + item_id).html(response.body['quantity']);
                $("#total-" + item_id).html(response.body['total']);
                $("#cart-total").html(response.body['cart_total']);
            });
    }

    decrease_quantity = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/decrease-item-quantity/" + item_id + "/", "POST", requestBody)
            .then(response => {
                if (response.status) {
                    $("#quantity-" + item_id).html(response.body['quantity']);
                    $("#total-" + item_id).html(response.body['total']);
                    $("#cart-total").html(response.body['cart_total']);
                }
            });
    }

    remove_from_cart_cart_html = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/delete-item/" + item_id + "/", "POST", requestBody)
            .then(response => {
                if (response.status) {
                    $("#item-" + item_id).remove();
                    const cart_item_count = $("#total-item-count").html();
                    $("#total-item-count").html(cart_item_count - 1);
                    $("#cart-total").html(response.body['cart_total']);
                    console.log(response.body['not_available'])
                    $("#pay_now_button").prop('disabled', response.body['not_available']);
                }
            });
    }
});