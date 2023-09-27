ADMIN_EMAIL = 'admin@admin.com'
CUSTOMER1_EMAIL = 'customer1@test.com'
CUSTOMER2_EMAIL = 'customer2@test.com'
CUSTOMER3_EMAIL = 'customer3@test.com'
CUSTOMER4_EMAIL = 'customer4@test.com'
AGENT1_EMAIL = 'agent1@test.com'
AGENT2_EMAIL = 'agent2@test.com'
AGENT3_EMAIL = 'agent3@test.com'
AGENT4_EMAIL = 'agent4@test.com'
AGENT5_EMAIL = 'agent5@test.com'
AGENT6_EMAIL = 'agent6@test.com'
RES1_EMAIL = 'res1@test.com'
RES2_EMAIL = 'res2@test.com'
RES3_EMAIL = 'res3@test.com'
RES4_EMAIL = 'res4@test.com'
RES6_EMAIL = 'res5@test.com'


# error templates
PAGE_NOT_FOUND_404_TEMPLATE = 'delivery_agent/404_not_found.html'
FORBIDDEN_403_TEMPLATE = 'delivery_agent/403_forbidden.html'

# accounts templates
LOGIN_TEMPLATE_NAME = 'accounts/login.html'
REGISTER_TEMPLATE_NAME = 'accounts/register.html'
FORGOT_PASS_TEMPLATE_NAME = 'accounts/forgot_password.html'
RESTORE_PASS_TEMPLATE_NAME = 'accounts/restore_password.html'
USER_PROFILE_TEMPLATE_NAME = 'accounts/user_profile.html'
AUTH_SETTINGS_TEMPLATE_NAME = 'accounts/settings.html'
SOCIAL_AUTH_PASS_TEMPLATE_NAME = 'accounts/set_social_auth_password.html'
UPDATE_ADDRESS_TEMPLATE_NAME = 'accounts/user_edit_address.html'


# admins templates
ADMIN_PANEL_TEMPLATE_NAME = 'admins/panel.html'
DRIVERS_LIST_TEMPLATE_NAME = 'admins/drivers.html'
DRIVERS_APPLICATION_LIST_TEMPLATE_NAME = 'admins/drivers-application.html'
DRIVERS_APPLICATION_DETAIL_TEMPLATE_NAME = 'admins/drivers-detail-application.html'
USERS_LIST_TEMPLATE_NAME = 'admins/users.html'
USERS_DETAIL_TEMPLATE_NAME = 'admins/users-detail.html'
RESTAURANT_LIST_TEMPLATE_NAME = 'admins/restaurants.html'
RESTAURANT_APPLICATION_LIST_TEMPLATE_NAME = 'admins/restaurants-application.html'
COD_AGENT_LIST_TEMPLATE_NAME = 'admins/cod-agents.html'
COD_AGENT_DETAIL_TEMPLATE_NAME = 'admins/cod-agent-detail.html'
RESTAURANT_DETAIL_TEMPLATE_NAME = 'admins/restaurants-detail.html'
RESTAURANT_APPLICATION_DETAIL_TEMPLATE_NAME = 'admins/restaurants-detail-application.html'
ORDERS_LIST_TEMPLATE_NAME = 'admins/orders.html'
ORDERS_DETAIL_TEMPLATE_NAME = 'admins/order-detail.html'


# Description:
# 1 Admin
# User_id = 1
COMMON_FIXTURE0 = 'common/admin.json'

# Description:
# 1 Active customer
# User_id = 2, Address_id = 1
COMMON_CUSTOMER1 = 'common/customer1.json'

# Description:
# 1 Inactive customer
# User_id = 3, Address_id = 2, Activation_id = 1
COMMON_CUSTOMER2 = 'common/customer2.json'

# Description:
# 1 Active and Blocked customer
# User_id = 4, Address_id = 3
COMMON_CUSTOMER3 = 'common/customer3.json'

# Description:
# 1 Inactive and Unverified agent
# User_id = 5, Address_id = 4, Activation_id = 2
COMMON_AGENT1 = 'common/agent1.json'

# Description:
# 1 Active and Unverified agent
# User_id = 6, Address_id = 5
COMMON_AGENT2 = 'common/agent2.json'

# Description:
# 1 Active, Blocked and Unverified agent
# User_id = 7, Address_id = 6
COMMON_AGENT3 = 'common/agent3.json'

# Description:
# 1 Active, Verified agent and Available
# User_id = 8, Address_id = 7(Ahmedabad)
COMMON_AGENT4 = 'common/agent4.json'

# Description:
# 1 Active, Blocked and Verified agent
# User_id = 9, Address_id = 8
COMMON_AGENT5 = 'common/agent5.json'

# Description:
# 1 Inactive restaurant owner with 1 Unverified Restaurant
# User_id = 10, Address_id = 9, Restaurant_id = 1, Activation_id = 3
COMMON_RESTAURANT1 = 'common/restaurant1.json'

# Description:
# 1 Active restaurant owner with 1 Unverified Restaurant
# User_id = 11, Address_id = 10, Restaurant_id = 2
COMMON_RESTAURANT2 = 'common/restaurant2.json'

# Description:
# 1 Active, Blocked restaurant owner with 1 Unverified Restaurant
# User_id = 12, Address_id = 11, Restaurant_id = 3
COMMON_RESTAURANT3 = 'common/restaurant3.json'

# Description:
# 1 Active restaurant owner with 1 Verified Restaurant
# User_id = 13, Address_id = 12, Restaurant_id = 4
COMMON_RESTAURANT4 = 'common/restaurant4.json'

# Description:
# 1 Active restaurant owner with 1 Verified and Blocked Restaurant
# User_id = 14, Address_id = 13, Restaurant_id = 5
COMMON_RESTAURANT5 = 'common/restaurant5.json'

# Description:
# 1 Active restaurant owner with 1 Verified Restaurant(Ahmedabad) with three items and is accepting orders
# User_id = 15, Address_id = 14, Restaurant_id = 6, Items_id=1,2,3
COMMON_RESTAURANT6 = 'common/restaurant6.json'

# Description:
# 1 Active restaurant owner with 1 Verified Restaurant(Mumbai) with three items and is accepting orders
# User_id = 16, Address_id = 15, Restaurant_id = 7, Items_id=4,5,6
COMMON_RESTAURANT7 = 'common/restaurant7.json'

# Description:
# 1 Active restaurant owner with 1 Verified Restaurant(Mumbai) with three items and is not accepting orders
# User_id = 17, Address_id = 18, Restaurant_id = 8, Items_id=7,8,9
COMMON_RESTAURANT8 = 'common/restaurant8.json'

# Description:
# 1 Active restaurant owner with 1 Verified and Blocked Restaurant(Ahmedabad)
# with three items and is not accepting orders
# User_id = 18, Address_id = 17, Restaurant_id = 9, Items_id=10,11,12
COMMON_RESTAURANT9 = 'common/restaurant9.json'

# Description:
# (Duplicate of COMMON_RESTAURANT6)
# 1 Active restaurant owner with 1 Verified Restaurant(Ahmedabad) with three items and is accepting orders
# User_id = 19, Address_id = 18, Restaurant_id = 10, Items_id=13,14,15
COMMON_RESTAURANT10 = 'common/restaurant10.json'

# Description:
# (Duplicate of COMMON_AGENT4)
# 1 Active and Verified agent(Ahmedabad)
# User_id = 20, Address_id = 19
COMMON_AGENT6 = 'common/agent6.json'

# Description:
# (Duplicate of COMMON_AGENT4)
# 1 Active and Verified agent(Mumbai)
# User_id = 21, Address_id = 20
COMMON_AGENT7 = 'common/agent7.json'

# Description:
# (Duplicate of COMMON_CUSTOMER1)
# 1 Active customer
# User_id = 22, Address_id = 21
COMMON_CUSTOMER4 = 'common/customer4.json'

# Orders fixture

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_AGENT4
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
THREE_ORDERS_DELIVERED_AND_ONE_PICKED = 'orders/three_delivered_and_one_picked_order_for_same_restaurants.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_AGENT6
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
ORDER_FOR_SAME_RESTAURANTS = 'orders/order_for_same_restaurants.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_AGENT6
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
ORDER_FOR_DIFFERENT_RESTAURANTS = 'orders/order_for_different_restaurants.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_AGENT6
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
PAYMENT_OF_TWO_ORDER_FOR_SAME_RESTAURANTS = 'orders/payment_of_two_order_for_same_restaurants.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_AGENT6
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
TWO_ORDER_FOR_SAME_RESTAURANTS = 'orders/two_order_for_same_restaurants.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_AGENT4
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS = 'orders/two_delivered_order_for_same_restaurants.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
ONE_ACCEPTED_ORDER_BY_AGENT = 'orders/one_accepted_order_by_agent.json'


# cart module constants

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_RESTAURANT9
#
CART_ITEMS_FOR_BLOCKED_RESTAURANTS = "carts/cart_items_for_blocked_restaurants.json"

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_RESTAURANT8
# COMMON_CUSTOMER1
CART_ITEMS_FOR_RESTAURANT_NOT_ACCEPTING_ORDER = 'carts/cart_items_for_restaurant_not_accepting_order.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
CART_ITEMS_NOT_AVAILABLE_QUANTITY_WISE = "carts/cart_items_not_available_quantity_wise.json"

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_RESTAURANT6, COMMON_RESTAURANT7
# COMMON_CUSTOMER1
CART_ITEMS_OF_DIFFERENT_RESTAURANTS = 'carts/cart_items_of_different_restaurants.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_RESTAURANT7
# COMMON_CUSTOMER1
CART_ITEMS_OF_NOT_AVAILABLE_LOCATION_WISE = 'carts/cart_items_of_not_available_location_wise.json'

# Description:
# load some agent, customer and restaurant fixtures before loading below fixture
# COMMON_RESTAURANT6
# COMMON_CUSTOMER1
CART_ITEMS_OF_VALID_RESTAURANT = "carts/cart_items_of_valid_restaurant.json"
