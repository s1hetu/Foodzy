$(document).ready(function () {
    // JavaScript wrapper function to send HTTP requests using Django's "X-CSRFToken" request header
    function sendHttpAsync(path, method, body) {
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
                $("#quantity-"+item_id).html(response.body['quantity']);
                $("#total-"+item_id).html(response.body['total']);
            });
    }

    decrease_quantity = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/decrease-item-quantity/" + item_id + "/", "POST", requestBody)
            .then(response => {
                if(response.status) {
                    $("#quantity-" + item_id).html(response.body['quantity']);
                    $("#total-" + item_id).html(response.body['total']);
                }
            });
    }

    remove_from_cart_cart_html = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/delete-item/" + item_id + "/", "POST", requestBody)
            .then(response => {
                if (response.status) {
                    $("#item-"+item_id).remove();
                }
            });
    }
});