import os
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    UserProfile, Product, ElectronicsSpecification, SemesterBundle,
    StudentRequest, Review, Report, Rental, ServiceBooking
)

class UserRegistrationForm(forms.ModelForm):
    campus = forms.CharField(max_length=200, required=True, initial='Tech University Campus')
    phone_number = forms.CharField(max_length=20, required=False)
    whatsapp_number = forms.CharField(max_length=20, required=False, help_text="For direct buyer/seller WhatsApp communication")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Choose a secure password (min 6 characters)'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        help_texts = {
            'email': 'Use your college email (.edu / .ac.in) for automatic student verification!',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(disabled=True, required=False)

    class Meta:
        model = UserProfile
        fields = ['campus', 'phone_number', 'whatsapp_number', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell other students about yourself, your department, and year...'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'category', 'description', 'price', 'product_type',
            'condition', 'campus', 'buy_or_rent', 'rent_daily_rate',
            'rent_monthly_rate', 'is_urgent', 'primary_image',
            'digital_file', 'sample_preview_pdf',
            'service_rate_type', 'service_duration_info'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Detailed item description, including included accessories and item condition...'}),
            'price': forms.NumberInput(attrs={'placeholder': '₹ Selling Price or Base Fee'}),
            'rent_daily_rate': forms.NumberInput(attrs={'placeholder': '₹ Per Day'}),
            'rent_monthly_rate': forms.NumberInput(attrs={'placeholder': '₹ Per Month'}),
        }

    def clean_primary_image(self):
        img = self.cleaned_data.get('primary_image')
        if img and hasattr(img, 'name'):
            ext = os.path.splitext(img.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValidationError("Allowed image formats: JPG, JPEG, PNG, WEBP.")
            if img.size > 15 * 1024 * 1024:
                raise ValidationError("Image size cannot exceed 15MB.")
        return img

    def clean_sample_preview_pdf(self):
        pdf = self.cleaned_data.get('sample_preview_pdf')
        if pdf and hasattr(pdf, 'name'):
            ext = os.path.splitext(pdf.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError("Sample preview must be a PDF file.")
            if pdf.size > 20 * 1024 * 1024:
                raise ValidationError("Sample preview cannot exceed 20MB.")
        return pdf

    def clean_digital_file(self):
        f = self.cleaned_data.get('digital_file')
        if f and hasattr(f, 'name'):
            ext = os.path.splitext(f.name)[1].lower()
            allowed = ['.pdf', '.zip', '.rar', '.7z', '.tar', '.gz', '.docx', '.ipynb', '.epub']
            if ext not in allowed:
                raise ValidationError(f"Allowed digital asset formats: {', '.join(allowed)}.")
            if f.size > 50 * 1024 * 1024:
                raise ValidationError("Digital asset size cannot exceed 50MB.")
        return f

    def clean(self):
        cleaned_data = super().clean()
        product_type = cleaned_data.get('product_type')
        buy_or_rent = cleaned_data.get('buy_or_rent')
        rent_daily_rate = cleaned_data.get('rent_daily_rate')

        if buy_or_rent in ['RENT', 'BOTH'] and not rent_daily_rate:
            self.add_error('rent_daily_rate', "Daily rental rate is required for rental listings.")

        return cleaned_data


class ElectronicsSpecificationForm(forms.ModelForm):
    class Meta:
        model = ElectronicsSpecification
        fields = [
            'processor', 'ram_gb', 'storage_gb', 'storage_type',
            'battery_health_percent', 'usage_duration_months',
            'display_specs', 'graphics', 'operating_system', 'extra_specs'
        ]
        widgets = {
            'processor': forms.TextInput(attrs={'placeholder': 'e.g. Apple M1 / Intel Core i5-1135G7'}),
            'display_specs': forms.TextInput(attrs={'placeholder': 'e.g. 13.3-inch Retina True Tone / 15.6" FHD 144Hz'}),
            'extra_specs': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Included charger, bill, box, ports, cycle count...'}),
        }


class SemesterBundleForm(forms.ModelForm):
    class Meta:
        model = SemesterBundle
        fields = ['title', 'semester', 'course', 'price', 'campus', 'description', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List everything included in this bundle (Books, printed notes, lab coats, tools)...'}),
        }


class StudentRequestForm(forms.ModelForm):
    class Meta:
        model = StudentRequest
        fields = ['title', 'category', 'max_budget', 'campus', 'contact_preference', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Need 5th Sem DBMS textbook by Korth'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Mention author, edition, or urgent deadline...'}),
            'max_budget': forms.NumberInput(attrs={'placeholder': '₹ Maximum budget'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(1, '1 ★ - Poor'), (2, '2 ★ - Fair'), (3, '3 ★ - Good'), (4, '4 ★ - Very Good'), (5, '5 ★ - Excellent')]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your experience with this item and seller...'}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Please explain why you are reporting this listing...'}),
        }


class RentalRequestForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['start_date', 'end_date', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Preferred meetup spot on campus or handover time...'}),
        }


class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = ['preferred_date', 'preferred_time', 'estimated_hours', 'client_notes']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TextInput(attrs={'placeholder': 'e.g. 4:00 PM - 5:00 PM'}),
            'client_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your doubts, project requirements, or syllabus...'}),
        }


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Your Full Name'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Mobile Number for Handover'}))
    campus = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'College Campus'}))
    delivery_location_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Hostel name & room no., Library entrance, or Student Canteen'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('COD', 'Cash on Campus Handover (COD)'),
            ('RAZORPAY', 'Online Payment via Razorpay'),
        ],
        widget=forms.RadioSelect,
        initial='COD'
    )
