from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator

from FDA.constants import DELIVERY_AGENT_ADDRESS_TITLE, ACCOUNT_INVALID_STATE_ERROR, ACCOUNT_INVALID_CITY_ERROR
from accounts.forms import RegisterForm
from accounts.models import Address, User
from restaurant.validators import validate_ifsc_code
from .models import Document
from .validators import validate_license_no, validate_pancard_no


class UserForm(RegisterForm):
    def save(self, **kwargs):
        email = self.data.get('email')
        password = self.data.get('password1')
        data = {
            'username': self.data.get('username'),
            'mobile_number': self.data.get('mobile_number'),
            'profile_pic': self.data.get('profile_pic'),
        }

        user = User.objects.create_delivery_agent(email=email, password=password, **data)
        user.is_active = False
        user.save()
        return user


class DocumentForm(forms.Form):
    license_number = forms.CharField(label='Driving Licence Number', validators=[validate_license_no],
                                     help_text="Enter 16 character Licenese number. e.g. HR-0619850034761")
    license_document = forms.ImageField(label='Driving Licence', help_text="Upload Front Image of Driving Licence")
    pancard_number = forms.CharField(label='PanCard Number', validators=[validate_pancard_no],
                                     help_text="Enter 10 digit PAN card number.  e.g. BNZAA2318J")
    pancard_document = forms.ImageField(label='PanCard', help_text="Upload Front Image of Pan card")
    account_no = forms.CharField(label="Bank Account Number", help_text='Enter 8 to 18 digit bank account number',
                                 validators=[MinLengthValidator(8), MaxLengthValidator(18)], max_length=18)
    ifsc_code = forms.CharField(label="IFSC Code", max_length=11, help_text='Enter 11 digit bank\'s IFSC Code',
                                validators=[validate_ifsc_code])

    def save(self, **kwargs):
        agent = kwargs['agent']
        return Document.objects.create(agent=agent, **self.cleaned_data)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'street', 'landmark', 'pincode', 'city', 'state']

    def save(self, **kwargs):
        address = Address.objects.create(address_title=DELIVERY_AGENT_ADDRESS_TITLE, **self.cleaned_data)
        user = kwargs['agent']
        user.addresses.add(address)
        return address

    def clean(self):
        super(AddressForm, self).clean()

        # validate pin code
        pin_code = self.cleaned_data.get('pincode')
        if len(str(pin_code)) != 6:
            self.add_error('pincode', "Invalid pincode")

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
        return self.cleaned_data
