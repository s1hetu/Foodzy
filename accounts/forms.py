from django import forms

from FDA.constants import (
    ACCOUNT_ALREADY_EXIST_EMAIL, ACCOUNT_PASSWORD_NOT_MATCHING, ACCOUNT_EMAIL_NOT_REGISTERED,
    ACCOUNT_EMAIL_NOT_VERIFIED, ACCOUNT_INCORRECT_PASSWORD, ACCOUNT_ALREADY_ACTIVE_EMAIL, ACCOUNT_PASSWORD_REQUIRED,
    ACCOUNT_EMAIL_BLOCKED, ACCOUNT_CUSTOMERS_ADDRESS_TITLE, ACCOUNT_PASSWORD_1_HELP_TEXT, ACCOUNT_EMAIL_HELP_TEXT,
    ACCOUNT_INVALID_CITY_ERROR, ACCOUNT_INVALID_STATE_ERROR, ACCOUNT_OLD_PASSWORD_LABEL, ACCOUNT_NEW_PASSWORD_LABEL,
    ACCOUNT_AGAIN_NEW_PASSWORD_LABEL, ACCOUNT_PROFILE_IMAGE_LABEL, ACCOUNT_PROFILE_IMAGE_ERROR, ACCOUNT_LAT_LONG_ERROR
)
from .models import User, Address
from .validations import validate_password


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        help_text=ACCOUNT_EMAIL_HELP_TEXT
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        validators=[validate_password],
        help_text=ACCOUNT_PASSWORD_1_HELP_TEXT
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(),
        required=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile_number', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.data.get('email')
        if email in User.get_user_emails():
            self.add_error('email', ACCOUNT_ALREADY_EXIST_EMAIL)
        return email

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', ACCOUNT_PASSWORD_NOT_MATCHING)
        return password2

    def save(self, **kwargs):
        email = self.data.get('email')
        password = self.data.get('password1')
        data = {
            'username': self.data.get('username'),
            'mobile_number': self.data.get('mobile_number'),
            'profile_pic': self.data.get('profile_pic'),
        }

        user = User.objects.create_user(email=email, password=password, **data)
        user.is_active = False
        user.save()

        return user


class CustomerAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'street', 'landmark', 'pincode', 'city', 'state', 'lat', 'long']

        widgets = {'lat': forms.HiddenInput(), 'long': forms.HiddenInput()}

    def save(self, **kwargs):
        address = Address.objects.create(address_title=ACCOUNT_CUSTOMERS_ADDRESS_TITLE, **self.cleaned_data)
        user = kwargs['user']
        user.addresses.add(address)
        return address

    def clean(self):
        super(CustomerAddressForm, self).clean()
        pin_code = self.cleaned_data.get('pincode')
        if len(str(pin_code)) != 6:
            self.add_error('pincode', "Invalid pincode. Enter a valid pin code like 360007.")

        # validating state and city
        state = self.cleaned_data.get('state')
        city = self.cleaned_data.get('city')

        if not state:
            self._errors['state'] = self.error_class([ACCOUNT_INVALID_STATE_ERROR])

        if not city:
            self._errors['city'] = self.error_class([ACCOUNT_INVALID_CITY_ERROR])

        if state and city and state.id != city.state_id:
            self._errors['state'] = self.error_class([ACCOUNT_INVALID_STATE_ERROR])
            self._errors['city'] = self.error_class([ACCOUNT_INVALID_CITY_ERROR])

        # validating lat and long
        lat = self.cleaned_data.get('lat')
        long = self.cleaned_data.get('long')
        if not lat or not long:
            self._errors['lat'] = self.error_class([ACCOUNT_LAT_LONG_ERROR])
        return self.cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email not in User.get_user_emails():
            self.add_error('email', ACCOUNT_EMAIL_NOT_REGISTERED)
        elif not User.is_active_user(email=email):
            self.add_error('email', ACCOUNT_EMAIL_NOT_VERIFIED)
        elif User.is_blocked_user(email=email):
            self.add_error('email', ACCOUNT_EMAIL_BLOCKED)

        return email

    def clean_password(self):
        password = self.data.get('password')
        email = self.data.get('email')

        query = User.is_active_user(email=email)
        if query and not User.get_user_from_email(email=email).check_password(password):
            self.add_error('password', ACCOUNT_INCORRECT_PASSWORD)

        return password


class ResendActivationCodeForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email not in User.get_user_emails():
            self.add_error('email', ACCOUNT_EMAIL_NOT_REGISTERED)
        elif User.is_active_user(email=email):
            self.add_error('email', ACCOUNT_ALREADY_ACTIVE_EMAIL)

        return email


class PasswordResetForm(forms.Form):
    old_password = forms.CharField(
        label=ACCOUNT_OLD_PASSWORD_LABEL,
        widget=forms.PasswordInput(),
        required=False
    )
    password1 = forms.CharField(
        label=ACCOUNT_NEW_PASSWORD_LABEL,
        widget=forms.PasswordInput(),
        required=True,
        validators=[validate_password],
        help_text=ACCOUNT_PASSWORD_1_HELP_TEXT)
    password2 = forms.CharField(
        label=ACCOUNT_AGAIN_NEW_PASSWORD_LABEL,
        widget=forms.PasswordInput(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.data.get('old_password')

        if not old_password:
            self.add_error('old_password', ACCOUNT_PASSWORD_REQUIRED)

        if not self.user.check_password(old_password):
            self.add_error('old_password', ACCOUNT_INCORRECT_PASSWORD)

        return old_password

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', ACCOUNT_PASSWORD_NOT_MATCHING)
        return password2

    def save(self, user):
        password = self.data.get('password1')
        user.set_password(password)
        user.save()
        return user


class PasswordRestoreForm(forms.Form):
    password1 = forms.CharField(
        label=ACCOUNT_NEW_PASSWORD_LABEL,
        widget=forms.PasswordInput(),
        required=True,
        validators=[validate_password],
        help_text=ACCOUNT_PASSWORD_1_HELP_TEXT)
    password2 = forms.CharField(
        label=ACCOUNT_AGAIN_NEW_PASSWORD_LABEL,
        widget=forms.PasswordInput(),
        required=True
    )

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', ACCOUNT_PASSWORD_NOT_MATCHING)
        return password2

    def save(self, user):
        password = self.data.get('password1')
        user.set_password(password)
        user.save()
        return user


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email not in User.get_user_emails():
            self.add_error('email', ACCOUNT_EMAIL_NOT_REGISTERED)
        elif User.is_inactive_user(email=email):
            self.add_error('email', ACCOUNT_EMAIL_NOT_VERIFIED)

        return email


class PasswordChangeForm(forms.Form):
    password1 = forms.CharField(
        label=ACCOUNT_NEW_PASSWORD_LABEL,
        widget=forms.PasswordInput(),
        required=True,
        validators=[validate_password],
        help_text=ACCOUNT_PASSWORD_1_HELP_TEXT)
    password2 = forms.CharField(
        label=ACCOUNT_AGAIN_NEW_PASSWORD_LABEL,
        widget=forms.PasswordInput(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', ACCOUNT_PASSWORD_NOT_MATCHING)
        return password2

    def save(self):
        password = self.data.get('password1')
        self.user.set_password(password)
        self.user.save()


class UserProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(
        label=ACCOUNT_PROFILE_IMAGE_LABEL,
        required=False,
        error_messages={'invalid': ACCOUNT_PROFILE_IMAGE_ERROR},
        widget=forms.FileInput
    )
    remove_photo = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'profile_pic', 'mobile_number']

    def save(self, commit=True):
        instance = super(UserProfileForm, self).save(commit=False)
        if self.cleaned_data.get('remove_photo'):
            # delete image <REMAINING>
            instance.profile_pic = None
        if commit:
            instance.save()
        return instance


class CustomerAddressUpdateForm(CustomerAddressForm):

    def save(self, **kwargs):
        self.instance.save()
