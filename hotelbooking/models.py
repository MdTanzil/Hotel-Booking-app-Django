from django.db import models
from ckeditor.fields import RichTextField


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(
        default=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Room_category(BaseModel):
    name = models.CharField(max_length=100)
    desc = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Room_view(BaseModel):
    name = models.CharField(max_length=100)
    desc = models.TextField()

    def __str__(self):
        return self.name


class Room(BaseModel):
    room_name = models.CharField(max_length=50)
    room_price = models.DecimalField(max_digits=11, decimal_places=2)
    max_person = models.IntegerField(default=1)
    room_size = models.IntegerField()
    room_desc = RichTextField()
    room_category = models.ForeignKey(Room_category, on_delete=models.CASCADE)
    room_view = models.ManyToManyField(Room_view)
    room_bed = models.IntegerField(default=1)
    room_image = models.ImageField(
        upload_to=None, height_field=None, width_field=None, max_length=None
    )

    def __str__(self):
        return self.room_name


class Package_item(BaseModel):
    item_name = models.CharField(max_length=50)

    def __str__(self):
        return self.item_name


class Package(BaseModel):
    name = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    price = models.IntegerField(default=100)
    package_item = models.ManyToManyField(Package_item)
    package_image = models.ImageField(
        "package", upload_to=None, height_field=None, width_field=None, max_length=None
    )

    def __str__(self):
        return self.name


class Booking(BaseModel):
    start_date = models.DateField()
    end_date = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.room.room_name


class Package_Booking(BaseModel):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)


class Guest(BaseModel):
    guest_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    nid_number = models.IntegerField(default=0)
    passport = models.CharField(max_length=15)
    permanent_address = models.TextField(blank=True)
    post_code = models.CharField(max_length=5)

    def __str__(self):
        return self.guest_name


class Lead(BaseModel):
    start_date = models.DateField()
    end_date = models.DateField()
    adult_member = models.IntegerField(default=1)
    child = models.IntegerField(default=0)
    room_01 = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_01")
    room_02 = models.ForeignKey(
        Room, on_delete=models.CASCADE, blank=True, null=True, related_name="room_02"
    )
    room_03 = models.ForeignKey(
        Room, on_delete=models.CASCADE, blank=True, null=True, related_name="room_03"
    )
    guest = models.ManyToManyField(Guest)

class Contact(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    def __str__(self):
        return self.name