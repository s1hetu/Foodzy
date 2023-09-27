from django.urls import reverse, resolve

from admins.views import (
    AdminPanel, DriversListView, CodAgentListView, DriversApplicationListView, DriversDetailView,
    CodAgentDetailView, DriversApplicationDetailView, UsersListView, UsersDetailView,
    RestaurantListView, RestaurantApplicationListView, RestaurantsDetailView, RestaurantsApplicationDetailView,
    OrdersListView, OrdersDetailView, ActionForRestaurantView, ActionForDeliveryAgentView, ActionForCustomerView,
    ActionForCodDeliveryAgentView, ApplicationActionForDeliveryAgentView, ApplicationActionForRestaurantView
)


class TestAdminUrls:
    def test_home_url(self):
        home_url = reverse('admin-home')
        assert resolve(home_url).func.view_class == AdminPanel

    def test_drivers_list_url(self):
        drivers_list_url = reverse('drivers-list')
        assert resolve(drivers_list_url).func.view_class == DriversListView

    def test_cod_agents_list_url(self):
        cod_agents_list_url = reverse('cod-agents-list')
        assert resolve(cod_agents_list_url).func.view_class == CodAgentListView

    def test_drivers_list_application_url(self):
        drivers_list_application_url = reverse('drivers-list-application')
        assert resolve(drivers_list_application_url).func.view_class == DriversApplicationListView

    def test_drivers_detail_url(self):
        drivers_detail_url = reverse('drivers-detail', kwargs={'pk': 1})
        assert resolve(drivers_detail_url).func.view_class == DriversDetailView

    def test_cod_agent_detail_url(self):
        cod_agent_detail_url = reverse('cod-agent-detail', kwargs={'pk': 1})
        assert resolve(cod_agent_detail_url).func.view_class == CodAgentDetailView

    def test_drivers_detail_application_url(self):
        drivers_detail_application_url = reverse('drivers-detail-application', kwargs={'pk': 1})
        assert resolve(drivers_detail_application_url).func.view_class == DriversApplicationDetailView

    def test_users_list(self):
        users_list_url = reverse('users-list')
        assert resolve(users_list_url).func.view_class == UsersListView

    def test_users_detail_url(self):
        users_detail_url = reverse('users-detail', kwargs={'pk': 1})
        assert resolve(users_detail_url).func.view_class == UsersDetailView

    def test_restaurant_list_url(self):
        restaurant_list_url = reverse('restaurant-list')
        assert resolve(restaurant_list_url).func.view_class == RestaurantListView

    def test_restaurant_list_application_url(self):
        restaurant_list_application_url = reverse('restaurant-list-application')
        assert resolve(restaurant_list_application_url).func.view_class == RestaurantApplicationListView

    def test_restaurant_detail_url(self):
        restaurant_detail_url = reverse('restaurant-detail', kwargs={'pk': 1})
        assert resolve(restaurant_detail_url).func.view_class == RestaurantsDetailView

    def test_restaurant_detail_application_url(self):
        restaurant_detail_application_url = reverse('restaurant-detail-application', kwargs={'pk': 1})
        assert resolve(restaurant_detail_application_url).func.view_class == RestaurantsApplicationDetailView

    def test_orders_list_url(self):
        orders_list_url = reverse('orders-list')
        assert resolve(orders_list_url).func.view_class == OrdersListView

    def test_orders_detail_url(self):
        orders_detail_url = reverse('orders-detail', kwargs={'pk': 1})
        assert resolve(orders_detail_url).func.view_class == OrdersDetailView

    def test_action_for_restaurant_url(self):
        action_for_restaurant_url = reverse('action-for-restaurant', kwargs={'pk': 1})
        assert resolve(action_for_restaurant_url).func.view_class == ActionForRestaurantView

    def test_action_for_delivery_agent_url(self):
        action_for_delivery_agent_url = reverse('action-for-delivery-agent', kwargs={'pk': 1})
        assert resolve(action_for_delivery_agent_url).func.view_class == ActionForDeliveryAgentView

    def test_action_for_customer_url(self):
        action_for_customer_url = reverse('action-for-customer', kwargs={'pk': 1})
        assert resolve(action_for_customer_url).func.view_class == ActionForCustomerView

    def test_action_for_cod_delivery_agent(self):
        action_for_cod_delivery_agent = reverse('action-for-cod-delivery-agent', kwargs={'pk': 1})
        assert resolve(action_for_cod_delivery_agent).func.view_class == ActionForCodDeliveryAgentView

    def test_application_action_for_delivery_agent(self):
        application_action_for_delivery_agent = reverse('application-action-for-delivery-agent', kwargs={'pk': 1})
        assert resolve(application_action_for_delivery_agent).func.view_class == ApplicationActionForDeliveryAgentView

    def test_application_action_for_restaurant_url(self):
        application_action_for_restaurant_url = reverse('application-action-for-restaurant', kwargs={'pk': 1})
        assert resolve(application_action_for_restaurant_url).func.view_class == ApplicationActionForRestaurantView
