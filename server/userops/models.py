from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

phone_regex_validator = RegexValidator(
    regex=r'^\+?[1-9]\d{7,14}$',
    message="Phone number must be entered in the format: '+999999999'. 8 to 15 digits allowed.",
    code="invalid_phone_number"
)
class App_users(AbstractUser):
    # =========================================================================
    # INHERITED FIELDS FROM AbstractUser (Included Automatically):
    # =========================================================================
    #
    # --- Authentication & Identity ---
    # username         = models.CharField(max_length=150, unique=True)
    # password         = models.CharField(max_length=128)
    # first_name       = models.CharField(max_length=150, blank=True)
    # last_name        = models.CharField(max_length=150, blank=True)
    # email            = models.EmailField(blank=True) # Overridden below to be unique/required
    #
    # --- Permissions & Status ---
    # is_staff         = models.BooleanField(default=False)  # Controls Django Admin access
    # is_active        = models.BooleanField(default=True)   # Soft deletion flag
    # is_superuser     = models.BooleanField(default=False)  # Grants all permissions automatically
    #
    # --- Groups & Object Permissions (from PermissionsMixin) ---
    # groups           = models.ManyToManyField(Group, related_name="user_set", blank=True)
    # user_permissions = models.ManyToManyField(Permission, related_name="user_set", blank=True)
    #
    # --- Dates & Auditing ---
    # last_login       = models.DateTimeField(blank=True, null=True)
    # date_joined      = models.DateTimeField(default=timezone.now)
    # =========================================================================

    class Roles(models.TextChoices):
        USER = "USER", "User"
        ADMIN = "ADMIN", "Admin"

    # Custom Field Overrides & Additions
    email = models.EmailField(unique=True, null=False, blank=False)
    user_roles = models.CharField(max_length=10, choices=Roles.choices, default=Roles.USER)
    institution = models.CharField(max_length=120, blank=True, null=True)
    phone = models.CharField(max_length=17,validators=[phone_regex_validator],blank=True)
    
    @property
    def what_role(self):
        return self.user_roles