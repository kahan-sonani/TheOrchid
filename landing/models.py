from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.CharField(max_length=122)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.name


class OUserManager(BaseUserManager):
    def create_user(self, email, mobileno, fname, lname ,password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            mobileno=mobileno,
            fname=fname,
            lname=lname
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password, mobileno, fname, lname):
        user = self.create_user(
            email,
            password=password,
            mobileno=mobileno,
            fname=fname,
            lname=lname
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, mobileno, fname, lname):
        user = self.create_user(
            email,
            password=password,
            mobileno=mobileno,
            fname=fname,
            lname=lname
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

    def create_users(self, email, password, mobileno, fname, lname):
        user = self.create_user(email, password=password, mobileno=mobileno, fname=fname, lname=lname)
        user.staff = False
        user.admin = False
        user.save(using=self.db)
        return user


class OUser(AbstractBaseUser):
    fname = models.CharField(max_length=122)
    lname = models.CharField(max_length=122)

    is_busy = models.BooleanField(default=True)
    is_verified = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)
    email = models.EmailField(max_length=155)
    mobileno = models.CharField(primary_key=True, max_length=10)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'mobileno'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['fname', 'lname', 'email']

    def get_first_name(self):
        return self.fname

    def get_short_name(self):
        return self.fname

    def __str__(self):
        return self.mobileno

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    objects = OUserManager()
