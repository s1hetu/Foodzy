# ACCOUNTS VARIABLE
ACCOUNT_REGISTER_SUCCESS = 'Successfully registered. To activate please verify email.'
ACCOUNT_ACTIVATION_SUCCESS = 'Successfully account activated.'
ACCOUNT_ACTIVATION_FAILED = 'Activation code is expired. You can apply for resend code for activation.'
ACCOUNT_MODEL_BACKEND = 'django.contrib.auth.backends.ModelBackend'
ACCOUNT_LOGIN_SUCCESS = 'Successfully logged in.'
ACCOUNT_LOGIN_FAILED = 'Invalid credentials.'
ACCOUNT_LOGOUT_SUCCESS = 'Successfully logged out.'
ACCOUNT_RESENT_ACTIVATION = 'Re-sent account activation code.'
ACCOUNT_PASSWORD_RESET_SUCCESS = 'Password reset successful. You must login again.'
ACCOUNT_USER_PROFILE_SUCCESS = 'Profile updated.'
ACCOUNT_USER_ADDRESS_SUCCESS = 'Address updated.'
ACCOUNT_PASSWORD_RESET_LINK_SENT = 'Link for password reset sent to your email.'
ACCOUNT_PASSWORD_RESET_INVALID_LINK = 'This link is invalid or expired. You can apply for resend.'
ACCOUNT_DEACTIVATION_SUCCESS = 'Successfully account deactivated.'

# ACCOUNTS MIXINS VARIABLE
ACCOUNT_MUST_BE_ANONYMOUS_USER = 'Sorry but you cannot view this page, as you are already logged in.'

# ACCOUNTS TEMPLATE PATH VARIABLE
ACCOUNT_LOGIN_PAGE = 'accounts/login.html'
ACCOUNT_REGISTER_PAGE = 'accounts/register.html'
ACCOUNT_SOCIAL_AUTH_MANAGE_PAGE = 'accounts/settings.html'
ACCOUNT_SOCIAL_AUTH_SET_PASSWORD_PAGE = 'accounts/set_social_auth_password.html'
ACCOUNT_FORGOT_PASSWORD_PAGE = 'accounts/forgot_password.html'
ACCOUNT_RESTORE_PASSWORD_PAGE = 'accounts/restore_password.html'
ACCOUNT_RESET_PASSWORD_PAGE = 'accounts/reset_password.html'
ACCOUNT_RESEND_ACTIVATION_CODE_PAGE = 'accounts/resend_activation_code.html'
ACCOUNT_USER_PROFILE_PAGE = 'accounts/user_profile.html'
ACCOUNT_USER_EDIT_ADDRESS_PAGE = 'accounts/user_edit_address.html'
ACCOUNT_USER_ACTIVATED_PAGE = 'accounts/activated.html'

# ACCOUNTS SOCIAL AUTH PROVIDERS
ACCOUNT_SOCIAL_AUTH_GITHUB = 'github'
ACCOUNT_SOCIAL_AUTH_TWITTER = 'twitter'
ACCOUNT_SOCIAL_AUTH_FACEBOOK = 'facebook'
ACCOUNT_SOCIAL_AUTH_GOOGLE = 'google-oauth2'

# ACCOUNTS FORMS VARIABLES
ACCOUNT_ALREADY_EXIST_EMAIL = 'This email is already registered.'
ACCOUNT_PASSWORD_NOT_MATCHING = 'The password is not matching.'
ACCOUNT_EMAIL_NOT_REGISTERED = 'This email is not registered.'
ACCOUNT_EMAIL_NOT_VERIFIED = 'The email is not verified.'
ACCOUNT_EMAIL_BLOCKED = 'The email is blocked.'
ACCOUNT_INCORRECT_PASSWORD = 'The password is incorrect.'
ACCOUNT_ALREADY_ACTIVE_EMAIL = 'This email is already active.'
ACCOUNT_PASSWORD_REQUIRED = 'Password is Required.'
ACCOUNT_CUSTOMERS_ADDRESS_TITLE = 'Customers Address'
ACCOUNT_PASSWORD_1_HELP_TEXT = 'Password must have one small letter, one capital letter, one number and one special character. Minimum password length is 7.'
ACCOUNT_EMAIL_HELP_TEXT = 'Example: useremail@gmail.com'
ACCOUNT_INVALID_STATE_ERROR = 'Invalid state and city.'
ACCOUNT_INVALID_CITY_ERROR = 'Selected city is not inside the given state.'
ACCOUNT_OLD_PASSWORD_LABEL = 'Current Password'
ACCOUNT_NEW_PASSWORD_LABEL = 'New Password'
ACCOUNT_AGAIN_NEW_PASSWORD_LABEL = 'Re-enter New Password'
ACCOUNT_PROFILE_IMAGE_LABEL = 'Profile Image'
ACCOUNT_PROFILE_IMAGE_ERROR = 'Profile image should be image file only.'
ACCOUNT_LAT_LONG_ERROR = 'Please select your location.'
ACCOUNT_MIN_2_LENGTH_ERROR = 'The field must contain at least 2 characters'

USER_TYPES = ['customer', 'restaurant_owner', 'delivery_agent', 'admin']

# RESTAURANT FORMS VARIABLE
RESTAURANT_ADDRESS_TITLE = 'Restaurant Address'

# RESTAURANT ITEM MODEL CHOICE FIELD
RESTAURANT_ITEM_MODEL_UNIT_CHOICE = (
    ("grams", "grams"), ("kilograms", "kilograms"), ("litres", "litres"), ("millilitres", "millilitres"),
    ("plate", "plate"), ("piece", "piece"))
RESTAURANT_RESTAURANT_MODEL_STATUS_CHOICES = (
    ("pending", "pending"), ("approved", "approved"), ("rejected", "rejected"))
RESTAURANT_RESTAURANT_MODEL_DEFAULT_IMAGE = "restaurant_images/restaurant_image.jpeg"
RESTAURANT_RESTAURANT_MODEL_IMAGE_UPLOAD_TO_PATH = 'restaurant_images/'
RESTAURANT_DOCUMENTS_MODEL_PAN_CARD_UPLOAD_TO_PATH = 'pan_cards/'
RESTAURANT_DOCUMENTS_MODEL_GST_CERTIFICATES_UPLOAD_TO_PATH = 'gst_certificates/'
RESTAURANT_DOCUMENTS_MODEL_FSSAI_CERTIFICATES_UPLOAD_TO_PATH = 'fssai_certificates/'
RESTAURANT_ITEMS_MODEL_DEFAULT_IMAGE = "static/restaurant/images/item_image.jpeg"
RESTAURANT_ITEMS_MODEL_IMAGE_UPLOAD_TO_PATH = 'item_images/'
RESTAURANT_GALLERY_MODEL_DEFAULT_IMAGE = "restaurant_gallery_images/restaurant_image.jpeg"
RESTAURANT_GALLERY_MODEL_IMAGE_UPLOAD_TO_PATH = 'restaurant_gallery_images/'

# RESTAURANT TEMPLATE PATH VARIABLE
RESTAURANT_OWNER_PANEL_PAGE = 'restaurant/owner_pannel.html'
RESTAURANT_PANEL_PAGE = 'restaurant/restaurant_pannel.html'
RESTAURANT_UPDATE_ITEM_PAGE = 'restaurant/update_items.html'
RESTAURANT_REGISTRATION_PAGE = 'restaurant/restaurant_registration.html'
RESTAURANT_ADD_RESTAURANT_PAGE = 'restaurant/add_restaurant.html'
RESTAURANT_MENU_PAGE = 'restaurant/restaurant_menu.html'
RESTAURANT_ORDERS_PAGE = 'restaurant/orders.html'
RESTAURANT_REVIEWS_PAGE = 'restaurant/reviews.html'
RESTAURANT_DETAIL_ORDER_PAGE = 'restaurant/detail_order.html'
RESTAURANT_STATUS_PAGE = 'restaurant/restaurant_status.html'
RESTAURANT_ADD_GALLERY_IMAGE_PAGE = 'restaurant/add_gallery_image.html'
RESTAURANT_VIEW_GALLERY_IMAGE_PAGE = 'restaurant/view_gallery.html'
RESTAURANT_EARNING_PAGE = 'restaurant/restaurant_earning.html'
RESTAURANT_ADD_ITEM_PAGE = 'restaurant/add_item.html'

# RESTAURANT VARIABLE
RESTAURANT_ACCOUNT_REGISTER_SUCCESS = 'Successfully registered your Restaurant. To activate please verify email.'
RESTAURANT_STATUS_UPDATED = "Status Updated Successfully!!"
RESTAURANT_ADDED_SUCCESSFULLY = "Restaurant added successfully"
RESTAURANT_IMAGE_ADDED_SUCCESSFULLY = "Image Uploaded Successfully!!"
RESTAURANT_ITEM_ADDED_SUCCESSFULLY = "Item added successfully."

# RESTAURANT PERMISSION
RESTAURANT_VIEW_RESTAURANT_PERMISSION = 'restaurant.view_restaurant'
RESTAURANT_VIEW_DOCUMENTS_PERMISSION = 'restaurant.view_documents'
RESTAURANT_UPDATE_RESTAURANT_ACCEPTING_ORDER_PERMISSION = 'restaurant.change_is_accepting_orders_on_restaurant'
RESTAURANT_ADD_ITEM_PERMISSION = 'restaurant.add_items'
RESTAURANT_UPDATE_IEM_PERMISSION = 'restaurant.change_items'
RESTAURANT_ADD_RESTAURANT_PERMISSION = 'restaurant.add_restaurant'
RESTAURANT_VIEW_ITEMS_PERMISSION = 'restaurant.view_items'
ORDERS_VIEW_ORDER_PERMISSION = 'orders.view_order'
ORDERS_CHANGE_ORDER_PERMISSION = 'orders.change_order'
RESTAURANT_VIEW_RATINGSANDREVIEWS_PERMISSION = 'restaurant.view_ratingsandreviews'
RESTAURANT_ADD_RESTAURANTGALLERY_PERMISSION = 'restaurant.add_restaurantgallery'
RESTAURANT_VIEW_RESTAURANTGALLERY_PERMISSION = 'restaurant.view_restaurantgallery'

# CARTS RESPONSES
CART_ITEM_DELETE_SUCCESS = 'Item removed from cart.'
NOT_AVAILABLE = "Product %s is not available..................... "
NOT_AVAILABLE_QUANTITY = "Product %s is not available in this quantity.................."
CART_EMPTY = "The cart is empty, Please add items to the cart"

# ADMINS VARIABLES
CANNOT_BLOCK_RESTAURANT_ERROR = "You cannot block restaurant as it has pending orders."
CONTACT_NOT_CREATED_ERROR = "Contact was not created due to some errors."
FUND_NOT_CREATED_ERROR = "Fund account was not created due to some errors."

# ADMINS TEMPLATE PATH VARIABLE
ADMINS_HOME_PAGE = 'admins/panel.html'
ADMINS_DRIVERS_LIST_PAGE = 'admins/drivers.html'
ADMINS_DRIVERS_APPLICATION_LIST_PAGE = 'admins/drivers-application.html'
ADMINS_DRIVERS_APPLICATION_DETAIL_PAGE = 'admins/drivers-detail-application.html'
ADMINS_DRIVERS_DETAIL_PAGE = 'admins/drivers-detail.html'
ADMINS_USERS_LIST_PAGE = 'admins/users.html'
ADMINS_USERS_DETAIL_PAGE = 'admins/users-detail.html'
ADMINS_RESTAURANT_LIST_PAGE = 'admins/restaurants.html'
ADMINS_RESTAURANT_DETAIL_PAGE = 'admins/restaurants-detail.html'
ADMINS_RESTAURANT_APPLICATION_LIST_PAGE = 'admins/restaurants-application.html'
ADMINS_RESTAURANT_APPLICATION_DETAIL_PAGE = 'admins/restaurants-detail-application.html'
ADMINS_ORDERS_LIST_PAGE = 'admins/orders.html'
ADMINS_ORDERS_DETAIL_PAGE = 'admins/order-detail.html'
ADMINS_COD_AGENTS_LIST_PAGE = 'admins/cod-agents.html'
ADMINS_COD_AGENTS_DETAIL_PAGE = 'admins/cod-agent-detail.html'

# ADMINS PAGINATION VARIABLE
DEFAULT_PAGINATED_BY = 5
DEFAULT_GET_ELIDED_PAGE_RANGE_ON_EACH_SIDE = 1
DEFAULT_GET_ELIDED_PAGE_RANGE_ON_ENDS = 0

# GENERAL
BAD_REQUEST = "Invalid request"

NARATION_RESTAURANT = "Payment transfer restaurant"
NARATION_AGENT = "Payment transfer agent"
PURPOSE = "payout"
MODE = "IMPS"
CURRENCY = "INR"
ACCOUNT_NUMBER = "2323230020156176"

# DELIVERY AGENT PATH VARIABLE
AGENT_REGISTRATION_FORM_PAGE = 'delivery_agent/registration.html'
AGENT_LIST_ACCEPTED_ORDERS_PAGE = 'delivery_agent/list_accepted_orders.html'
AGENT_CURRENT_DELIVERIES_PAGE = 'delivery_agent/current_deliveries.html'
AGENT_SEE_AVAILABLE_DELIVERIES_PAGE = 'delivery_agent/see_available_deliveries.html'
AGENT_REVIEWS_PAGE = 'delivery_agent/reviews.html'
AGENT_DETAIL_ORDER_PAGE = 'delivery_agent/detail_order.html'
AGENT_TIME_ENTRY_PAGE = 'delivery_agent/time_entries.html'
AGENT_APPLICATION_STATUS_PAGE = 'delivery_agent/agent_application_status.html'
AGENT_NOT_AVAILABLE_PAGE = 'delivery_agent/agent_not_Available.html'
AGENT_EARNING_PAGE = 'delivery_agent/agent_earning.html'
AGENT_GET_COORDINATES_PAGE = 'delivery_agent/get_coordinates.html'
AGENT_PANEL_PAGE = 'delivery_agent/panel.html'

# DELIVERY AGENT FORMS VARIABLE
DELIVERY_AGENT_ADDRESS_TITLE = 'Delivery Agent Address'

# DELIVERY_AGENT SERVICE
PAYMENT_RECEIVED_SUCCESSFULLY = "Payment Received Successfully!"
ORDER_NOT_DELIVERED = "Order is not delivered yet!"
ALREADY_UPDATED = "This field is already updated"
REQUIRED_FIELD = "This Field is required!"
DELIVERY_ACCEPTED = "Delivery Accepted Successfully!"
DELIVERY_ALREADY_ACCEPTED = "Oops! Delivery is already accepted !!"
ALREADY_AN_ACCEPTED_ORDER = 'You have some Orders to deliver first'
STATUS_UPDATED = 'Status Updated Successfully!'
CAN_NOT_ACCEPT_WAITING_CANCELLED_OR_REJECTED_ORDER = 'Can not accept cancelled order or order contains rejected or ' \
                                                     'waiting status ! '
OTP_NOT_FOUND = 'No otp found, resend otp and try again.'
WRONG_OTP = 'OTP is incorrect'
ORDER_DELIVERED = 'Order delivered successfully!'
OTP_RESEND = 'Resend OTP successfully! '
ITEM_NOT_AVAILABLE_LOCATION_WISE = "item: {} is not eligible for delivery, it's to far "

# ORDER TEMPLATE PATH VARIABLE
ORDER_DETAIL_ORDER_PAGE = 'orders/detail_order.html'
ORDER_ORDER_PAGE = 'orders/orders.html'
ORDER_PAY_NOW_PAGE = 'orders/pay_now.html'
ORDER_INVOICE_PAGE = 'customers/invoice.html'
VALID_ORDER_DISTANCE = 10
ERR_PAYMENT_EVENT_NOT_DEFINE = "Pyment Event is not Define"

ORDER_CALLBACK_URL = 'http://127.0.0.1:8000/order/order_paid/'

# ORDER VARIABLES
ORDER_PLACED_MESSAGE = "%s orders has been placed."
ORDER_PAYMENT_SUCCESSFUL = "Order payment successful............................"
ORDER_PAYMENT_FAILED = "Order payment failed............................Please retry after few minutes."

# CUSTOMER TEMPLATE PATH VARIABLE
CUSTOMER_ITEM_LIST_PAGE = 'customers/item_list.html'
CUSTOMER_CART_PAGE = 'customers/cart.html'
CUSTOMER_ITEM_DETAIL_PAGE = 'customers/item_detail.html'
CUSTOMER_RATING_PAGE = 'customers/rating.html'

# CUSTOMER CONSTANT VARIABLE
EMPTY_RATING_MESSAGE = 'Hey ! Rating can not be empty !'
INVALID_RATING_MESSAGE = 'Ratings should be in 0.5-5'
