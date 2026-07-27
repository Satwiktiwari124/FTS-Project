from django.db import models


class adminlogin(models.Model):
    username = models.CharField(max_length=225)
    password = models.CharField(max_length=16)
    create_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username



# USER LOGIN MODEL


class userlogin(models.Model):
    username = models.CharField(max_length=225)
    email = models.EmailField(max_length=225)
    password = models.CharField(max_length=16)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

# EMPLOYEE MODEL

class addemployee(models.Model):
    name = models.CharField(max_length=225)
    username = models.CharField(max_length=225)
    email = models.EmailField(max_length=100)
    mobile = models.CharField(max_length=15)
    empid = models.CharField(max_length=50)
    department = models.CharField(max_length=500)
    designation = models.CharField(max_length=225)
    role = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    password = models.CharField(max_length=16)
    photo = models.ImageField(upload_to='profile/')
    address = models.CharField(max_length=500)

    def __str__(self):
        return self.name

# DEPARTMENT MODEL

class adddepartment(models.Model):
    department_name = models.CharField(max_length=225)
    department_code = models.CharField(max_length=20)
    dep_head = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    dep_email = models.CharField(max_length=100)
    dep_number = models.CharField(max_length=12)

    def __str__(self):
        return self.department_name

# FILE UPLOAD MODEL

class Fileupload(models.Model):
    file_no = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    priority = models.CharField(max_length=50)
    create_user = models.CharField(max_length=100, null=True, blank=True)
    departments = models.CharField(max_length=100, null=True, blank=True)
    current_user = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_no

        
class FileMovement(models.Model):
    file = models.ForeignKey(Fileupload, on_delete=models.CASCADE)
    from_user = models.CharField(max_length=100)
    to_user = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    moved_at = models.DateTimeField(auto_now_add=True)