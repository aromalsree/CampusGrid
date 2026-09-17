import uuid
from decimal import Decimal
from django import forms
from django.utils.text import slugify
from .models import Listing, Category


class ListingForm(forms.ModelForm):
    """
    Form for students to create and publish listings on the CampusGrid marketplace.
    Excludes internal fields like seller, status, and timestamps.
    Automatically assigns unique slug and enforces campus validation.
    """

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        empty_label="Select a campus category",
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'id_category',
        }),
        help_text="Select the faculty domain or category that best fits your listing."
    )

    class Meta:
        model = Listing
        fields = [
            'title',
            'category',
            'listing_type',
            'description',
            'price',
            'rental_period',
            'condition',
            'location',
            'is_negotiable',
            'is_urgent',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MacBook Pro M1 16GB, Stewart Calculus 8th Edition',
                'id': 'id_title',
                'autocomplete': 'off',
            }),
            'listing_type': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'id_listing_type',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detail condition, included accessories, edition, syllabus relevance, semester usage, or pickup instructions...',
                'rows': 5,
                'id': 'id_description',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'id': 'id_price',
            }),
            'rental_period': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'id_rental_period',
            }),
            'condition': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'id_condition',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Engineering Hostel 3, Central Library, Tech Quad',
                'id': 'id_location',
            }),
            'is_negotiable': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
                'id': 'id_is_negotiable',
            }),
            'is_urgent': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
                'id': 'id_is_urgent',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

        # Human-friendly field labels
        self.fields['title'].label = "Listing Title"
        self.fields['category'].label = "Category"
        self.fields['listing_type'].label = "What type of listing is this?"
        self.fields['description'].label = "Description & Details"
        self.fields['price'].label = "Price (₹)"
        self.fields['rental_period'].label = "Rental Billing Period"
        self.fields['condition'].label = "Physical Item Condition"
        self.fields['location'].label = "Campus Pickup / Handover Spot"
        self.fields['is_negotiable'].label = "Price is negotiable"
        self.fields['is_urgent'].label = "Mark as urgent (moving-out / rapid clearance)"

        # Helpful choices with placeholders for optional fields
        self.fields['condition'].choices = [("", "Select condition (if physical item)")] + list(Listing.Condition.choices)
        self.fields['rental_period'].choices = [("", "Select billing frequency (if renting)")] + list(Listing.RentalPeriod.choices)

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        return title

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 10:
            raise forms.ValidationError("Please provide a descriptive explanation (at least 10 characters).")
        return desc

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < Decimal('0.00'):
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get('listing_type')
        rental_period = cleaned_data.get('rental_period')

        # If listing is for rent, rental period should be specified
        if listing_type == Listing.ListingType.RENT:
            if not rental_period:
                self.add_error('rental_period', "Please specify a rental billing period (e.g. Per Day, Per Month, Per Semester).")

        return cleaned_data

    def save(self, commit=True):
        listing = super().save(commit=False)
        # Automatically generate clean unique URL slug from title if not set
        if not listing.slug:
            base_slug = slugify(listing.title) or "listing"
            unique_suffix = uuid.uuid4().hex[:6]
            listing.slug = f"{base_slug}-{unique_suffix}"
        if commit:
            listing.save()
            self.save_m2m()
        return listing


from .models import NeedRequest, NeedOffer


class NeedRequestForm(forms.ModelForm):
    """
    Form for students to broadcast a new urgent need request to campus peers.
    """
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        empty_label="Select relevant category (optional)",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'id_need_category',
        }),
        help_text="Helps peers browsing specific subjects or gear find your request."
    )

    class Meta:
        model = NeedRequest
        fields = [
            'title',
            'category',
            'request_type',
            'urgency',
            'max_budget',
            'is_budget_negotiable',
            'location',
            'description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Casio fx-991EX Calculator for Midterms, Stewart Calculus 8th Ed',
                'id': 'id_need_title',
                'autocomplete': 'off',
            }),
            'request_type': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'id_need_request_type',
            }),
            'urgency': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'id_need_urgency',
            }),
            'max_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00 (Optional)',
                'min': '0',
                'step': '0.01',
                'id': 'id_need_max_budget',
            }),
            'is_budget_negotiable': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
                'id': 'id_need_negotiable',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Central Library 2nd Floor, Academic Block 3, Tech Quad',
                'id': 'id_need_location',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detail your need: course code, exam deadline, return date if borrowing, required specifications...',
                'rows': 4,
                'id': 'id_need_description',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from django.db import connection
            if "market_category" in connection.introspection.table_names():
                self.fields['category'].queryset = Category.objects.filter(is_active=True)
            else:
                self.fields['category'].queryset = Category.objects.none()
        except Exception:
            self.fields['category'].queryset = Category.objects.none()

        self.fields['title'].label = "What do you urgently need?"
        self.fields['category'].label = "Category"
        self.fields['request_type'].label = "Request Type"
        self.fields['urgency'].label = "Urgency Level"
        self.fields['max_budget'].label = "Maximum Budget (₹)"
        self.fields['is_budget_negotiable'].label = "Budget is flexible / open to negotiation"
        self.fields['location'].label = "Preferred Campus Handover Spot"
        self.fields['description'].label = "Context & Detailed Requirements"

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise forms.ValidationError("Please provide a specific title (at least 3 characters).")
        return title

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 10:
            raise forms.ValidationError("Please provide some helpful context for peers (at least 10 characters).")
        return desc

    def clean_max_budget(self):
        budget = self.cleaned_data.get('max_budget')
        if budget is not None and budget < Decimal('0.00'):
            raise forms.ValidationError("Budget cannot be negative.")
        return budget


class NeedOfferForm(forms.ModelForm):
    """
    Form for peers to submit an offer or response to a NeedRequest.
    """
    class Meta:
        model = NeedOffer
        fields = ['message', 'offered_price']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain what you have, item condition, when you can meet on campus...',
                'id': 'id_offer_message',
            }),
            'offered_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Offer price in ₹ (optional if lending)',
                'min': '0',
                'step': '0.01',
                'id': 'id_offer_price',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].label = "Your Response / Offer Note"
        self.fields['offered_price'].label = "Your Proposed Price (₹, optional)"

