from django.db import models
import datetime

# Create your models here.
class Students(models.Model):
    name = models.CharField(max_length=100)

    roll_no = models.BigIntegerField(unique=True)

    face_embeddings = models.BinaryField()

    image = models.ImageField(upload_to="student_images/")

    def __str__(self):
        return f"{self.name} ({self.roll_no})"


class Attendance(models.Model):

    student = models.ForeignKey(Students,on_delete=models.CASCADE)

    date = models.DateTimeField(auto_now_add=True)

    time = models.TimeField(default=datetime.time(0, 0, 0))

    status = models.CharField(max_length=10, choices=[('Present', 'Present'),('Absent', 'Absent')],default="Present")

    class Meta:
        unique_together = ("student","date")

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
