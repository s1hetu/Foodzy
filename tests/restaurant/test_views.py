import json

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertRedirects, assertContains

from accounts.models import State, City, User
from orders.models import Order
from restaurant.models import Categories, Restaurant, Items
from tests.constants import (
    COMMON_RESTAURANT4, COMMON_RESTAURANT2, COMMON_RESTAURANT5,
    COMMON_RESTAURANT6, COMMON_RESTAURANT9, COMMON_CUSTOMER1,
    COMMON_CUSTOMER4, COMMON_RESTAURANT7, ORDER_FOR_DIFFERENT_RESTAURANTS,
    COMMON_AGENT4, PAGE_NOT_FOUND_404_TEMPLATE, FORBIDDEN_403_TEMPLATE
)

password = "Test@1234"


class TestRestaurantPanel:
    url = reverse('restaurant-admin')
    template_name = 'restaurant/owner_pannel.html'

    def test_get_request(self, load_data, login_user):
        load_data(COMMON_RESTAURANT4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(self.url)
        assert response.status_code == 200
        assertContains(response, 'restaurants')
        assert response.context['restaurants'].first().id == 4
        assertTemplateUsed(response, self.template_name)

    def test_get_request_without_login(self, load_data, client):
        response = client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={self.url}")


class TestOwnerPanel:
    template_name = 'restaurant/restaurant_pannel.html'

    def test_get_request(self, login_user, load_data):
        load_data(COMMON_RESTAURANT4)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant.owner.email, password=password)
        response = owner_admin.get(reverse('owner-admin', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assert response
        assertTemplateUsed(response, self.template_name)

    def test_get_request_with_no_restaurant_id(self, login_user, load_data):
        load_data(COMMON_RESTAURANT4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('owner-admin', kwargs={"pk": 100}))
        assert response.status_code == 404
        assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)

    def test_get_request_with_different_owner(self, login_user, load_data):
        load_data(COMMON_RESTAURANT4, COMMON_RESTAURANT2)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant.owner.email, password=password)
        response = owner_admin.get(reverse('owner-admin', kwargs={"pk": 2}))
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)


class TestUpdateRestaurantAcceptingOrderStatus:
    restaurant4 = COMMON_RESTAURANT4

    def test_get_request(self, login_user, load_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('restaurant-status', kwargs={"pk": restaurant.id}))
        assert response.status_code == 405

    def test_update_status_success(self, login_user, load_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(reverse('restaurant-status', kwargs={"pk": restaurant.id}), data={'status': True})
        assert response.status_code == 200

    def test_update_status_invalid_restaurant_id(self, login_user, load_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(reverse('restaurant-status', kwargs={"pk": 100}))
        assert response.status_code == 404
        assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)

    def test_update_status_restaurant_blocked(self, login_user, load_data):
        load_data(COMMON_RESTAURANT5)
        restaurant_owner = User.objects.get(id=14)
        restaurant = Restaurant.objects.get(id=5)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(reverse('restaurant-status', kwargs={"pk": restaurant.id}), data={'status': True})
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)

    # def test_update_status_restaurant_not_blocked(self, login_user, load_data):  #     load_data('restaurant/1A_1D(UI)_1D(UA)_1C(A)_4R(VA)_1R(UA)_2RR(A_same_city).json')  #     restaurant_owner = User.objects.get(id=5)  #     restaurant = Restaurant.objects.get(id=1)  #     owner_admin, owner = login_user(restaurant_owner.email, password=password)  #     response = owner_admin.post(reverse('restaurant-status', kwargs={"pk": 100}))  #     assert response.status_code == 404  #     assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)


class TestAddItem:
    restaurant4 = COMMON_RESTAURANT4
    template_name = 'restaurant/add_item.html'

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('add-item', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_add_item_success(self, load_data, login_user, get_item_form_initial_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        data = get_item_form_initial_data()
        data['category'] = Categories.objects.get(id=1).id
        response = owner_admin.post(reverse('add-item', kwargs={"pk": restaurant.id}), data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('restaurant-menu', kwargs={"pk": restaurant.id}))

    @pytest.mark.parametrize('invalid_data',
                             [{'quantity': "abc"}, {'price': "abc"}, {'unit': "abc"}, {'discount': "abc"}])
    def test_add_item_invalid_data(self, load_data, login_user, invalid_data, get_item_form_initial_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        data = get_item_form_initial_data(**invalid_data)
        data['category'] = Categories.objects.get(id=1).id
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(reverse('add-item', kwargs={"pk": restaurant.id}), data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_add_item_blank_form_submission(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(reverse('add-item', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_add_item_missing_parameter(self, load_data, login_user, get_item_form_initial_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        item_data = get_item_form_initial_data()
        item_data['category'] = Categories.objects.get(id=1).id
        del item_data['name']
        response = owner_admin.post(reverse('add-item', kwargs={"pk": restaurant.id}), data=item_data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestUpdateItem:
    template_name = 'restaurant/update_items.html'
    restaurant6 = COMMON_RESTAURANT6

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant6)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        item = Items.objects.get(id=2)
        response = owner_admin.get(reverse('update-item', kwargs={"pk": item.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_with_invalid_item_id(self, load_data, login_user):
        load_data(self.restaurant6)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('update-item', kwargs={"pk": 100}))
        assert response.status_code == 404
        assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)

    def test_get_request_with_blocked_restaurant(self, load_data, login_user):
        load_data(COMMON_RESTAURANT9)
        restaurant_owner = User.objects.get(id=18)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        item = Items.objects.get(id=10)
        response = owner_admin.get(reverse('update-item', kwargs={"pk": item.id}))
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)

    def test_get_request_with_different_owner(self, load_data, login_user):
        load_data(self.restaurant6, COMMON_RESTAURANT5)
        restaurant_owner = User.objects.get(id=14)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        item = Items.objects.get(id=2)
        response = owner_admin.get(reverse('update-item', kwargs={"pk": item.id}))
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)

    def test_update_item_success(self, load_data, login_user, get_item_form_initial_data):
        load_data(self.restaurant6)
        restaurant_owner = User.objects.get(id=15)
        restaurant = Restaurant.objects.get(id=6)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        item = Items.objects.get(id=1)
        data = get_item_form_initial_data(name="paneer handi")
        data['category'] = Categories.objects.get(id=1).id
        response = owner_admin.post(reverse('update-item', kwargs={"pk": item.id}), data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('restaurant-menu', kwargs={"pk": restaurant.id}))

    @pytest.mark.parametrize('invalid_data', [{'quantity': 'abc'}])
    def test_update_item_invalid_data(self, load_data, login_user, get_item_form_initial_data, invalid_data):
        load_data(self.restaurant6)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        item = Items.objects.get(id=1)
        invalid_data = get_item_form_initial_data(**invalid_data)
        response = owner_admin.post(reverse('update-item', kwargs={"pk": item.id}), data=invalid_data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_update_item_blank_form_submission(self, load_data, login_user):
        load_data(self.restaurant6)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        item = Items.objects.get(id=2)
        response = owner_admin.post(reverse('update-item', kwargs={"pk": item.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_update_item_missing_parameter(self, load_data, login_user, get_item_form_initial_data):
        load_data(self.restaurant6)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        data = get_item_form_initial_data()
        item = Items.objects.get(id=1)
        response = owner_admin.post(reverse('update-item', kwargs={"pk": item.id}), data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestRegisterRestaurantView:
    url = reverse('register-restaurant')
    template_name = 'restaurant/restaurant_registration.html'

    def test_get_request(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_logged_in_user(self, client, login_user, load_data):
        load_data(COMMON_CUSTOMER1)
        user = User.objects.get(id=2)
        user_admin, user = login_user(email=user.email, password=password)
        response = user_admin.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    def test_restaurant_registration_success(self, client, get_restaurant_registration_form_initial_data):
        response = client.post(self.url,
                               data=get_restaurant_registration_form_initial_data(state=State.objects.get(id=1),
                                                                                  city=City.objects.get(id=1)))
        assert response.status_code == 302
        assertRedirects(response, reverse('login'))

    @pytest.mark.parametrize('invalid_data',
                             [{'pincode': 1234}, {'account_no': 123}, {'ifsc_code': '1'}, {'pan_card': "afkjwc"}])
    def test_restaurant_registration_invalid_data(self, invalid_data, client,
                                                  get_restaurant_registration_form_initial_data):
        data = get_restaurant_registration_form_initial_data(**invalid_data, state=State.objects.get(id=1),
                                                             city=City.objects.get(id=1))
        response = client.post(self.url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_restaurant_registration_blank_form_submission(self, client):
        url = reverse('register-restaurant')
        response = client.post(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_restaurant_registration_missing_parameter(self, client, get_restaurant_registration_form_initial_data):
        data = get_restaurant_registration_form_initial_data(state=State.objects.get(id=1), city=City.objects.get(id=1))
        del data['username']
        response = client.post(self.url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_user_registration_for_user_exists(self, client, get_restaurant_registration_form_initial_data):
        response = client.post(self.url, data=get_restaurant_registration_form_initial_data(email="rest11@gmail.com",
                                                                                            mobile_number="+918989898999",
                                                                                            state=State.objects.get(
                                                                                                id=1),
                                                                                            city=City.objects.get(
                                                                                                id=1)))
        assert response.status_code == 302
        assertRedirects(response, reverse('login'))

        response = client.post(self.url, data=get_restaurant_registration_form_initial_data(email="rest11@gmail.com",
                                                                                            mobile_number="+918989898999",
                                                                                            state=State.objects.get(
                                                                                                id=1),
                                                                                            city=City.objects.get(
                                                                                                id=1)))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestAddRestaurant:
    url = reverse('add-restaurant')
    restaurant4 = COMMON_RESTAURANT4
    template_name = 'restaurant/add_restaurant.html'

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_with_no_restaurants(self, load_data, login_user):
        load_data(COMMON_CUSTOMER1)
        user = User.objects.get(id=2)
        owner_admin, owner = login_user(email=user.email, password=password)
        response = owner_admin.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)

    def test_add_restaurant_success(self, load_data, login_user, get_add_restaurant_form_initial_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(self.url, data=get_add_restaurant_form_initial_data(state=State.objects.get(id=1),
                                                                                        city=City.objects.get(id=1)))

        assert response.status_code == 302
        assertRedirects(response, reverse('restaurant-admin'))

    def test_add_restaurant_missing_parameters(self, get_add_restaurant_form_initial_data, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        data = get_add_restaurant_form_initial_data(state=State.objects.get(id=1), city=City.objects.get(id=1))
        del data['name']
        response = owner_admin.post(self.url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    @pytest.mark.parametrize("invalid_data",
                             [{'pincode': 1234}, {'account_no': 123}, {'ifsc_code': '1'}, {'pan_card': "afkjwc"}])
    def test_add_restaurant_invalid_data(self, get_add_restaurant_form_initial_data, load_data, login_user,
                                         invalid_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        data = get_add_restaurant_form_initial_data(state=State.objects.get(id=1), city=City.objects.get(id=1),
                                                    **invalid_data)
        response = owner_admin.post(self.url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_add_restaurant_empty_form(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(self.url, data={})
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestRestaurantMenu:
    template_name = 'restaurant/restaurant_menu.html'
    restaurant6 = COMMON_RESTAURANT6

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant6)
        restaurant_owner = User.objects.get(id=15)
        restaurant = Restaurant.objects.get(id=6)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('restaurant-menu', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestViewOrders:
    template_name = "restaurant/orders.html"
    restaurant4 = COMMON_RESTAURANT4

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('view-orders', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestViewReviews:
    template_name = 'restaurant/reviews.html'
    restaurant4 = COMMON_RESTAURANT4

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant.owner.email, password=password)
        response = owner_admin.get(reverse('view-reviews', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestDetailOrder:
    order1 = (COMMON_RESTAURANT6, COMMON_RESTAURANT7,
              COMMON_CUSTOMER1, ORDER_FOR_DIFFERENT_RESTAURANTS)
    template_name = 'restaurant/detail_order.html'

    def test_get_request(self, load_data, login_user):
        load_data(self.order1)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        order = Order.objects.get(id=1)
        response = owner_admin.get(reverse('detail-order', kwargs={"pk": order.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_with_invalid_order_id(self, load_data, login_user):
        load_data(self.order1)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('detail-order', kwargs={"pk": 100}))
        assert response.status_code == 404
        assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)

    def test_get_request_with_different_user(self, load_data, login_user):
        load_data(self.order1, COMMON_CUSTOMER4)
        user = User.objects.get(id=22)
        order = Order.objects.get(id=1)
        user_admin, owner = login_user(user.email, password=password)
        response = user_admin.get(reverse('detail-order', kwargs={"pk": order.id}))
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)

    def test_update_order_status(self, load_data, login_user):
        load_data(self.order1)
        restaurant_owner = User.objects.get(id=15)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        order = Order.objects.get(id=1)
        response = owner_admin.post(reverse('detail-order', kwargs={"pk": order.id}),
                                    data=json.dumps({"status": "accepted"}), content_type="application/json")
        assert response.status_code == 200

        response2 = owner_admin.post(reverse('detail-order', kwargs={"pk": order.id}),
                                     data=json.dumps({"status": "rejected"}), content_type="application/json")
        assert response2.status_code == 200


class TestAddGalleryImage:
    template_name = 'restaurant/add_gallery_image.html'
    restaurant4 = COMMON_RESTAURANT4

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('add-gallery-image', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_add_gallery_image_success(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        file_name = "./media/default.jpg"
        response = owner_admin.post(reverse('add-gallery-image', kwargs={"pk": restaurant.id}),
                                    data={"image": (open(file_name, 'rb'), file_name)})
        assert response.status_code == 302
        assertRedirects(response, reverse('view_restaurant_gallery', kwargs={"pk": restaurant.id}))

    def test_add_gallery_empty_form(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(reverse('add-gallery-image', kwargs={"pk": restaurant.id}), data={})
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    @pytest.mark.parametrize("invalid_data", [{"image": "abc"}, {"image": 123}, {"cbbc": "323"}])
    def test_add_gallery_invalid_data(self, load_data, login_user, invalid_data):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.post(reverse('add-gallery-image', kwargs={"pk": restaurant.id}), data=invalid_data)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestViewGalleryImage:
    template_name = 'restaurant/view_gallery.html'
    restaurant4 = COMMON_RESTAURANT4

    def test_get_request_from_restaurant(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        client, owner = login_user(restaurant_owner.email, password=password)
        response = client.get(reverse('view_restaurant_gallery', kwargs={'pk': restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_from_user(self, load_data, login_user):
        load_data(COMMON_CUSTOMER1)
        user = User.objects.get(id=2)
        customer_client, user = login_user(user.email, password=password)
        response = customer_client.get(reverse('view_gallery'))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_from_agent(self, load_data, login_user):
        load_data(COMMON_AGENT4)
        user = User.objects.get(id=8)
        customer_client, user = login_user(user.email, password=password)
        response = customer_client.get(reverse('view_gallery'))
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)


class TestRestaurantEarningListView:
    template_name = 'restaurant/restaurant_earning.html'
    restaurant4 = COMMON_RESTAURANT4

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('restaurant-earning', kwargs={"pk": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestRestaurantStatusView:
    template_name = 'restaurant/restaurant_status.html'
    restaurant4 = COMMON_RESTAURANT4

    def test_get_request(self, load_data, login_user):
        load_data(self.restaurant4)
        restaurant_owner = User.objects.get(id=13)
        restaurant = Restaurant.objects.get(id=4)
        owner_admin, owner = login_user(restaurant_owner.email, password=password)
        response = owner_admin.get(reverse('restaurant-verification-status', kwargs={"restaurant_id": restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)
