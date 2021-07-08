from django.db import models

# Create your models here.
class StudentInfo(models.Model):
    """学生信息：演示多对多"""
    name = models.CharField(max_length=32, null=True, verbose_name='学生姓名')

    class Meta:
        db_table = 'tb_student_info'
    def __str__(self):
        return self.name

class CourseInfo(models.Model):
    """课程信息：演示多对多"""
    name = models.CharField(max_length=32, null=True, verbose_name='课程名字')
    students = models.ManyToManyField(StudentInfo)

    class Meta:
        db_table = 'tb_course_info'

    def __str__(self):
        return self.name