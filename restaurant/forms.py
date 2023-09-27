from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator

from FDA.constants import RESTAURANT_ADDRESS_TITLE
from accounts.forms import Address, User, CustomerAddressForm
from accounts.forms import RegisterForm
from .models import Restaurant, Documents, Items, RestaurantGallery
from .validators import validate_ifsc_code


class RestaurantUserForm(RegisterForm):
    def save(self, **kwargs):
        email = self.data.get('email')
        password = self.data.get('password1')
        data = {
            'username': self.data.get('username'),
            'mobile_number': self.data.get('mobile_number'),
            'profile_pic': self.data.get('profile_pic'),
        }

        user = User.objects.create_restaurant_owner(email=email, password=password, **data)
        user.is_active = False
        user.save()

        return user


class AddressForm(CustomerAddressForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'street', 'landmark', 'pincode', 'city', 'state', 'lat', 'long']
        widgets = {'lat': forms.HiddenInput(), 'long': forms.HiddenInput()}

    def save(self, **kwargs):
        return Address.objects.create(address_title=RESTAURANT_ADDRESS_TITLE, **self.cleaned_data)


class RestaurantForm(forms.Form):
    name = forms.CharField(max_length=50, label='Restaurant Name')
    image = forms.ImageField(label='Restaurant Image', help_text="Upload Image of your Restaurant")

    def save(self, **kwargs):
        address = kwargs['address']
        owner = kwargs['owner']
        return Restaurant.objects.create(owner=owner, address=address, **self.cleaned_data)


class DocumentsForm(forms.Form):
    account_no = forms.CharField(label="Bank Account Number", help_text='Enter 8 to 18 digit bank account number',
                                 validators=[MinLengthValidator(8), MaxLengthValidator(18)], max_length=18)
    ifsc_code = forms.CharField(label="IFSC Code", max_length=11, help_text='Enter 11 digit bank\'s IFSC Code',
                                validators=[validate_ifsc_code])
    pan_card = forms.ImageField(label='Pan Card', help_text="Upload Front Image of Pan card")
    gst_certificate = forms.ImageField(label="GST Certificate", help_text="Upload Front Image of GST Certificate")
    fssai_certificate = forms.ImageField(label="FSSAI Certificate", help_text="Upload Front Image of FSSAI Certificate")

    def save(self, **kwargs):
        restaurant = kwargs['restaurant']
        return Documents.objects.create(restaurant=restaurant, **self.cleaned_data)


class ItemForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = ['category', 'name', 'available_quantity', 'quantity', 'unit', 'price', 'description', 'image',
                  'discount']

    def save(self, **kwargs):
        pk = kwargs.get('pk')
        return Items.objects.create(restaurant_id=pk, **self.cleaned_data)


class GalleryImageForm(forms.Form):
    image = forms.ImageField(label='Image', help_text="Upload Image of restaurant")

    class Meta:
        model = RestaurantGallery
        fields = ['image']

    def save(self, **kwargs):
        return RestaurantGallery.objects.create(restaurant_id=kwargs.get('restaurant_id'), **self.cleaned_data)
