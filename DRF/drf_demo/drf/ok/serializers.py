from rest_framework import serializers
from .models import StudentInfo,CourseInfo


class Course(serializers.ModelSerializer):
    students = serializers.StringRelatedField(many=True)

    class Meta:
        model = CourseInfo
        fields = ['id','name','students']

class Student(serializers.ModelSerializer):
    courseinfo_set = serializers.StringRelatedField(many=True)
    class Meta:
        model = StudentInfo
        fields = ['id','name','courseinfo_set']