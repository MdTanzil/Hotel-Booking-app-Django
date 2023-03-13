from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True,blank=True,)
    class Meta:
        abstract = True


class Room_category(BaseModel):
    name = models.CharField(max_length=100)
    desc = models.TextField()
    def __str__(self):
        return self.name
    

class Room_view(BaseModel):
    name = models.CharField(max_length=100)
    desc = models.TextField()
    def __str__(self):
        return self.name
    


class Room(BaseModel):
    room_name = models.CharField( max_length=50)
    room_price = models.FloatField(default=0)
    max_person = models.IntegerField(default=1)
    room_size= models.IntegerField()
    room_desc = models.TextField()
    room_category = models.ForeignKey(Room_category, on_delete=models.CASCADE)
    room_view = models.ManyToManyField(Room_view)
    room_bed = models.IntegerField(default=1)
    room_image = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=None)
    def __str__(self):
        return self.room_name


class Package_item(BaseModel):
    item_name = models.CharField( max_length=50)

    def __str__(self):
        return self.item_name

class Package(BaseModel):
    name = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    price = models.IntegerField(default=100)
    package_item = models.ManyToManyField(Package_item)
    package_image = models.ImageField('package', upload_to=None, height_field=None, width_field=None, max_length=None)

    def __str__(self):
        return self.name
