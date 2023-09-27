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
                        .attr('class', 'btn btn-danger btn-lg')
                    const quantity_buttons = `
                        <div class="row">
                            <div class="col-6 col-sm-5 col-md-3 fw-bold">Total</div>
                            <div class="col-6 col-sm-7 col-md-8">&#8377; <span id="total-${item_id}">${response.body['total']}</span></div>
                        </div>
                        <hr>
                        <div class="row">
                            <div class="col-6 col-sm-5 col-md-3 fw-bold">Quantity</div>
                            <div class="col-6 col-sm-7 col-md-8">
                                <button class="btn" onclick="decrease_quantity(${item_id})">
                                    <h4 class="m-0 align-middle">-</h4>
                                </button>
                                <span id="quantity-${item_id}" class="border border-dark p-2 m-2 mx-2 h4 align-middle">1</span>
                                <button class="btn" onclick="increase_quantity(${item_id})">
                                    <h4 class="m-0 align-middle">+</h4>
                                </button>
                            </div>
                        </div>
                        <hr>
                    `
                    $("#cart-button")
                        .html(quantity_buttons)
                        .append(remove_from_cart_button)
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
                        .attr('class', 'btn btn-success btn-lg')
                    $("#cart-button").html(remove_from_cart_button)
                }
            });
    }

    increase_quantity = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/increase-item-quantity/" + item_id + "/", "POST", requestBody)
            .then(response => {
                console.log(response)
                $("#quantity-" + item_id).html(response.body['quantity']);
                $("#total-" + item_id).html(response.body['total']);
            });
    }

    decrease_quantity = (item_id) => {
        let requestBody = {};
        sendHttpAsync("/cart/decrease-item-quantity/" + item_id + "/", "POST", requestBody)
            .then(response => {
                if (response.status) {
                    $("#quantity-" + item_id).html(response.body['quantity']);
                    $("#total-" + item_id).html(response.body['total']);
                }
            });
    }
});