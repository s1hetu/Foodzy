from unittest.mock import patch

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from accounts.models import User, State, City
from tests.constants import (
    CUSTOMER1_EMAIL, COMMON_CUSTOMER1, AGENT2_EMAIL,
    COMMON_AGENT2, RES2_EMAIL, COMMON_RESTAURANT2, LOGIN_TEMPLATE_NAME,
    CUSTOMER2_EMAIL, COMMON_CUSTOMER2, COMMON_CUSTOMER3,
    CUSTOMER3_EMAIL, REGISTER_TEMPLATE_NAME,
    FORGOT_PASS_TEMPLATE_NAME, RESTORE_PASS_TEMPLATE_NAME,
    USER_PROFILE_TEMPLATE_NAME, AUTH_SETTINGS_TEMPLATE_NAME,
    SOCIAL_AUTH_PASS_TEMPLATE_NAME, UPDATE_ADDRESS_TEMPLATE_NAME
)


class TestLoginView:
    url = reverse('login')

    @pytest.mark.parametrize(('user_email', 'user_load_data'),
                             [
                                 (CUSTOMER1_EMAIL, COMMON_CUSTOMER1),
                                 (AGENT2_EMAIL, COMMON_AGENT2),
                                 (RES2_EMAIL, COMMON_RESTAURANT2),
                             ]
                             )
    def test_user_login_success(self, client, user_email, user_load_data, load_data, test_password):
        load_data(user_load_data)

        data = {
            'email': user_email,
            'password': test_password,
        }

        response = client.post(self.url, data=data)
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_valid_user_with_authentication_failed(self, client, test_password, load_data):
        load_data(COMMON_CUSTOMER1)

        with patch('accounts.services.authenticate') as mock_authenticate:
            mock_authenticate.return_value = False
            data = {'email': CUSTOMER1_EMAIL, 'password': test_password}
            response = client.post(self.url, data=data)
            assert response.status_code == 200
            assertTemplateUsed(response, LOGIN_TEMPLATE_NAME)
            assert 'Invalid credentials.' in [str(msg) for msg in response.context['messages']]

    @pytest.mark.django_db
    def test_user_login_invalid_password(self, client, test_password, load_data):
        load_data(COMMON_CUSTOMER1)

        data = {
            'email': CUSTOMER1_EMAIL,
            'password': 'WrongPassword'
        }
        url = reverse('login')
        response = client.post(url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, LOGIN_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_inactive_user_login(self, client, test_password, load_data):
        load_data(COMMON_CUSTOMER2)
        data = {
            'email': CUSTOMER2_EMAIL,
            'password': test_password
        }
        url = reverse('login')
        response = client.post(url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, LOGIN_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_blocked_user_login(self, client, test_password, load_data):
        load_data(COMMON_CUSTOMER3)

        data = {
            'email': CUSTOMER3_EMAIL,
            'password': test_password
        }

        url = reverse('login')
        response = client.post(url, data=data)

        assert response.status_code == 200
        assertTemplateUsed(response, LOGIN_TEMPLATE_NAME)

    def test_get_login_form(self, client):
        response = client.get(self.url)
        assert response.status_code == 200

    def test_user_login_invalid_email(self, client):
        data = {
            'email': 'test1@gmail.com',
            'password': 'Test@123'
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'invalid_data',
        [
            {'email': 'test@test.com'},
            {'password': 'test@123'},
        ]
    )
    def test_user_login_missing_parameter(self, client, invalid_data):
        response = client.post(self.url, data=invalid_data)
        assert response.status_code == 200


class TestLogoutView:
    @pytest.mark.django_db
    def test_logout_for_logged_in_user(self, login_user, test_password, load_data):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('logout')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.django_db
    def test_logout_for_anonymous_user(self, client):
        url = reverse('logout')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")


class TestRegisterView:
    url = reverse('register')

    def test_user_registration_for_user_exists(self, client, get_register_customer_user_initial_data, load_data):
        load_data(COMMON_CUSTOMER1)

        state = State.objects.get(name='Gujarat')
        city = City.objects.get(name='Ahmedabad')

        data = get_register_customer_user_initial_data(city=city, state=state, email=CUSTOMER1_EMAIL)

        response = client.post(self.url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, REGISTER_TEMPLATE_NAME)

    def test_get_request(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, REGISTER_TEMPLATE_NAME)

    def test_customer_registration_success(self, client, get_register_customer_user_initial_data):
        state = State.objects.get(name='Gujarat')
        city = City.objects.get(name='Ahmedabad')

        response = client.post(self.url, data=get_register_customer_user_initial_data(state, city))
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.parametrize(
        'invalid_data',
        [
            {'password1': 'test@123', 'password2': 'test@123'},
            {'password1': 'TEST@123', 'password2': 'TEST@123'},
            {'password1': 'Test123', 'password2': 'Test123'},
            {'password1': 'Complicated123', 'password2': 'Complicated123'},
            {'password1': 'Test@test', 'password2': 'Test@test'},
            {'password1': 'test@123', 'password2': 'test@23'},
            {'mobile_number': '7894561230'},
            {'email': 'testgmail.com'},
            {'pincode': '99'},
        ]
    )
    def test_customer_registration_invalid_data(
            self,
            invalid_data,
            client,
            get_register_customer_user_initial_data
    ):
        state = State.objects.get(name='Gujarat')
        city = City.objects.get(name='Ahmedabad')

        response = client.post(self.url, data=get_register_customer_user_initial_data(state, city, **invalid_data))
        assert response.status_code == 200
        assertTemplateUsed(response, REGISTER_TEMPLATE_NAME)

    def test_user_registration_blank_form_submission(self, client):
        url = reverse('register')
        response = client.post(url)
        assert response.status_code == 200
        assertTemplateUsed(response, REGISTER_TEMPLATE_NAME)

    def test_user_registration_missing_parameter(self, client, get_register_customer_user_initial_data):
        state = State.objects.get(name='Gujarat')
        city = City.objects.get(name='Ahmedabad')

        data = get_register_customer_user_initial_data(state, city)
        del data['username']
        response = client.post(self.url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, REGISTER_TEMPLATE_NAME)


class TestActivateView:
    @staticmethod
    def get_url(code='hgdjsd565dbsb5456'):
        return reverse('activate-api', kwargs={'code': code})

    def test_activate_success(self, client, load_data):
        load_data(COMMON_CUSTOMER2)
        code = '36c54215-296f-4fba-a7f7-c4e96004c231'

        with patch('accounts.services.Activation.is_valid') as mock_is_valid:
            mock_is_valid.return_value = True
            response = client.get(self.get_url(code))

            assert response.status_code == 200
            assert response.context['is_link_valid']

            user = User.objects.get(email=CUSTOMER2_EMAIL)
            assert user.is_active

    def test_activate_already_activated(self, client, load_data):
        load_data(COMMON_CUSTOMER1)
        code = '36c54215-296f-4fba-a7f7-c4e96004c231'

        url = self.get_url(code)
        response = client.get(url)
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_activate_fail(self, client, load_data):
        load_data(COMMON_CUSTOMER2)

        code = '36c54215-296f-4fba-a7f7-c4e96004c231'

        with patch('accounts.services.Activation.is_valid') as mock_is_valid:
            mock_is_valid.return_value = False
            response = client.get(self.get_url(code))

            assert response.status_code == 200
            assert not response.context['is_link_valid']

            user = User.objects.get(email=CUSTOMER2_EMAIL)
            assert not user.is_active

    def test_activate_failed(self, client):
        response = client.get(self.get_url())
        assert response.status_code == 404


class TestResendActivationCodeView:
    url = reverse('resend-activation-code-api')

    def test_reactivation_form_valid_email(self, client, load_data):
        load_data(COMMON_CUSTOMER2)
        data = {
            'email': CUSTOMER2_EMAIL
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 302

    def test_reactivation_form_valid_email_already_active(self, client, load_data):
        load_data(COMMON_CUSTOMER1)

        data = {
            'email': CUSTOMER1_EMAIL
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 200

    def test_get_reactivation_form(self, client):
        response = client.get(self.url)
        assert response.status_code == 200

    def test_reactivation_form_invalid_email(self, client):
        data = {
            'email': 'soni@gmail.com'
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 200

    def test_reactivation_blank_form(self, client):
        response = client.post(self.url, data={})
        assert response.status_code == 200


class TestDeactivateAccountView:
    @pytest.mark.django_db
    def test_user_account_deactivate_success(self, load_data, login_user, test_password):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('deactivate-api')
        response = client.get(url)

        assert response.status_code == 302
        assertRedirects(response, reverse('home'))
        user.refresh_from_db()
        assert not user.is_active

    @pytest.mark.django_db
    def test_user_account_deactivate_failed(self, client):
        url = reverse('deactivate-api')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")


class TestPasswordResetView:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'invalid_data', [
            {'old_password': '', 'password1': '', 'password2': ''},
            {'old_password': 'Test@123', 'password1': 'Test@123', 'password2': 'test123'},
            {'old_password': 'Test@123', 'password1': 'Test1234', 'password2': 'Test1234'},
            {'old_password': 'Test@123', 'password1': 'test@1234', 'password2': 'test@1234'},
            {'old_password': 'Test@123', 'password1': 'Test@test', 'password2': 'Test@test'},
        ]
    )
    def test_post_request_on_password_reset_fail(
            self,
            invalid_data,
            load_data,
            login_user,
            test_password
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('password-reset-api')
        response = client.post(url, data=invalid_data)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_post_request_on_password_reset_success(
            self,
            load_data,
            login_user,
            test_password
    ):
        load_data(COMMON_CUSTOMER1)
        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)

        data = {
            'old_password': test_password,
            'password1': 'Test@123',
            'password2': 'Test@123'
        }
        url = reverse('password-reset-api')
        response = client.post(url, data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.django_db
    def test_get_request_on_password_reset_form_fail(self, client):
        url = reverse('password-reset-api')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")

    @pytest.mark.django_db
    def test_post_request_on_password_reset_form_fail(self, client):
        data = {
            'old_password': 'test@123',
            'password1': 'Test@123',
            'password2': 'Test@123'
        }
        url = reverse('password-reset-api')
        response = client.post(url, data=data)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")


class TestForgotPasswordView:

    @pytest.mark.django_db
    def test_get_request_on_forgot_password_fail(
            self,
            load_data,
            login_user,
            test_password
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)

        url = reverse('forgot-password')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.django_db
    def test_post_request_on_forgot_password_fail_1(
            self,
            load_data,
            login_user,
            test_password
    ):
        """
        Test post request on Forgot password api with logged-in user.
        """
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)

        data = {
            'email': CUSTOMER1_EMAIL
        }
        url = reverse('forgot-password')
        response = client.post(url, data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.django_db
    def test_post_request_on_forgot_password_fail_2(
            self,
            load_data,
            client,
    ):
        """
        Test post request on Forgot password api with user without verification/activation.
        """
        load_data(COMMON_CUSTOMER2)

        data = {
            'email': CUSTOMER2_EMAIL
        }
        url = reverse('forgot-password')
        response = client.post(url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, FORGOT_PASS_TEMPLATE_NAME)

    def test_post_request_on_forgot_password_success(self, client, load_data):
        load_data(COMMON_CUSTOMER1)

        data = {'email': CUSTOMER1_EMAIL}

        url = reverse('forgot-password')

        response = client.post(url, data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    def test_get_request_on_forgot_password_success(self, client):
        url = reverse('forgot-password')
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, FORGOT_PASS_TEMPLATE_NAME)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'invalid_data',
        [
            {'email': 'abc@gmail.com'},
            {'email': 'abcgmail.com'},
            {'email': ''},
        ]
    )
    def test_forgot_password_request_inactive_user(self, client, invalid_data):
        url = reverse('forgot-password')
        response = client.post(url, data=invalid_data)
        assert response.status_code == 200
        assertTemplateUsed(response, FORGOT_PASS_TEMPLATE_NAME)


class TestRestorePasswordConfirmView:
    @pytest.mark.django_db
    def test_get_request_on_restore_password_confirm_view_success(
            self, client, load_data
    ):
        load_data(COMMON_CUSTOMER1)

        user = User.objects.get(email=CUSTOMER1_EMAIL)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('restore-password', kwargs={'uidb64': uid, 'token': token})
        response = client.get(url)

        assert response.status_code == 200
        assertTemplateUsed(response, RESTORE_PASS_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_post_request_on_restore_password_confirm_view_success(
            self, client, load_data, test_password
    ):
        load_data(COMMON_CUSTOMER1)

        user = User.objects.get(email=CUSTOMER1_EMAIL)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('restore-password', kwargs={'uidb64': uid, 'token': token})
        data = {
            'password1': test_password,
            'password2': test_password,
        }
        response = client.post(url, data=data)

        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.django_db
    def test_get_request_restore_password_confirm_view_active_user_invalid_token(
            self, client, load_data, test_password
    ):
        load_data(COMMON_CUSTOMER1)

        user = User.objects.get(email=CUSTOMER1_EMAIL)

        uid = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse('restore-password', kwargs={'uidb64': uid, 'token': 'abcdefgh-ij-klm-nop-qrs-tu-vwx-yz'})
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'invalid_data',
        [
            {'password1': 'Test@1234', 'password2': 'Test@123'},
            {'password1': '', 'password2': ''},
            {'password1': 'Test@1234'},
        ]
    )
    def test_post_request_on_restore_password_confirm_view_fail(
            self, client, load_data, test_password, invalid_data
    ):
        load_data(COMMON_CUSTOMER1)

        user = User.objects.get(email=CUSTOMER1_EMAIL)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('restore-password', kwargs={'uidb64': uid, 'token': token})

        response = client.post(url, data=invalid_data)

        assert response.status_code == 200
        assertTemplateUsed(response, RESTORE_PASS_TEMPLATE_NAME)


class TestUserProfileView:
    @pytest.mark.django_db
    def test_get_authorized_user_profile(self, load_data, login_user, test_password):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, USER_PROFILE_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_get_unauthorized_user_profile(self, client):
        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")

    @pytest.mark.django_db
    def test_update_unauthorized_user_profile(self, client):
        url = reverse('profile')
        response = client.post(url, data={})
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")

    @pytest.mark.django_db
    def test_update_authorized_user_profile_valid_data(
            self, load_data, login_user, test_password
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        data = {
            "username": "test_user",
            "mobile_number": "+919887654320",
            "profile_pic": "media/default.jpg"
        }
        url = reverse('profile')
        response = client.post(url, data=data)
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_update_authorized_user_profile_invalid_data(
            self, load_data, login_user, test_password
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        data = {
            "mobile_number": "+919887654320"
        }
        url = reverse('profile')
        response = client.post(url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, USER_PROFILE_TEMPLATE_NAME)


class TestSocialAuthManageSetting:
    @pytest.mark.django_db
    def test_social_auth_authorized_user(
            self, load_data, login_user, test_password
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('settings')
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, AUTH_SETTINGS_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_social_auth_unauthorized_user(self, client):
        url = reverse('settings')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")


class TestSocialAuthSetPassword:
    @pytest.mark.django_db
    def test_get_social_auth_set_password_form(
            self, load_data, login_user, test_password
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('password')
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, SOCIAL_AUTH_PASS_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_social_auth_set_password_valid_data(
            self, load_data, login_user, test_password,
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        data = {
            'password1': 'Test@123',
            'password2': 'Test@123'
        }
        url = reverse('password')
        response = client.post(url, data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('home'))

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'invalid_data',
        [
            {},
            {'password1': 'Test@1234', 'password2': 'Test@123'}
        ]
    )
    def test_social_auth_set_password_invalid_data(
            self, load_data, login_user, test_password, invalid_data
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('password')
        response = client.post(url, data=invalid_data)
        assert response.status_code == 200
        assertTemplateUsed(response, SOCIAL_AUTH_PASS_TEMPLATE_NAME)


class TestUserAddressUpdateView:
    @pytest.mark.django_db
    def test_get_request_on_user_address_update_success(
            self, load_data, login_user, test_password,
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('edit-address')
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, UPDATE_ADDRESS_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_get_request_on_user_address_update_wrong_user(
            self, load_data, login_user, test_password,
    ):
        load_data(COMMON_CUSTOMER1)
        load_data(COMMON_AGENT2)

        client, user = login_user(email=AGENT2_EMAIL, password=test_password)
        url = reverse('edit-address')
        response = client.get(url)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_post_request_on_user_address_update_success(
            self, load_data, login_user, test_password, get_address_form_initial_data
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        state = State.objects.get(name='Gujarat')
        city = City.objects.get(name='Ahmedabad')
        data = get_address_form_initial_data(city, state, address_line1='Update address_line1')

        url = reverse('edit-address')
        response = client.post(url, data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('edit-address'))
        assert user.addresses.first().address_line1 == 'Update address_line1'

    @pytest.mark.django_db
    def test_post_request_on_user_address_update_fail(
            self, load_data, login_user, test_password, get_address_form_initial_data
    ):
        load_data(COMMON_CUSTOMER1)

        client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        state = State.objects.get(name='Maharashtra')
        city = City.objects.get(name='Ahmedabad')
        data = get_address_form_initial_data(city, state)

        url = reverse('edit-address')
        response = client.post(url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, UPDATE_ADDRESS_TEMPLATE_NAME)

    @pytest.mark.django_db
    def test_get_request_on_user_address_update_success(self, client):
        url = reverse('edit-address')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")
