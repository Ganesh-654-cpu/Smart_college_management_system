from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from campus.models import (Attendance, Course, Department, Examination, Faculty, Fee, FeePayment,
                           Notice, Result, Student, Subject, TimetableEntry, User)

class Command(BaseCommand):
    help = "Create a small demo campus with sample administrator, faculty and student accounts."

    def handle(self, *args, **options):
        dept,_=Department.objects.get_or_create(code="CSE",defaults={"name":"Computer Science","description":"Computing and information technology"})
        course,_=Course.objects.get_or_create(code="BSC-CS",defaults={"name":"B.Sc. Computer Science","department":dept,"duration_years":3})
        def user(username, first, last, role, email):
            obj,_=User.objects.get_or_create(username=username,defaults={"first_name":first,"last_name":last,"role":role,"email":email,"is_active":True})
            obj.set_password("CampusDemo!26")
            if role == User.Role.ADMIN: obj.is_staff=True; obj.is_superuser=True
            obj.save()
            return obj
        admin_user=user("campusadmin","Campus","Admin",User.Role.ADMIN,"admin@example.test")
        faculty_user=user("faculty.demo","Aarav","Shah",User.Role.FACULTY,"faculty@example.test")
        student_user=user("student.demo","Mira","Patel",User.Role.STUDENT,"student@example.test")
        faculty,_=Faculty.objects.get_or_create(user=faculty_user,defaults={"department":dept,"qualification":"M.Sc. Computer Science","employee_id":"EMP-1001"})
        student,_=Student.objects.get_or_create(user=student_user,defaults={"course":course,"roll_number":"CS-026","enrollment_number":"SCMS-2026-0026","semester":1,"admission_date":date.today()})
        subject,_=Subject.objects.get_or_create(code="CS101",defaults={"course":course,"name":"Programming Fundamentals","semester":1,"faculty":faculty})
        exam,_=Examination.objects.get_or_create(name="Mid Semester",subject=subject,defaults={"exam_date":date.today()+timedelta(days=14),"max_marks":100})
        Result.objects.get_or_create(student=student,examination=exam,defaults={"marks":Decimal("86.00"),"published":True})
        Attendance.objects.get_or_create(student=student,subject=subject,date=date.today()-timedelta(days=1),defaults={"status":Attendance.Status.PRESENT,"marked_by":faculty})
        fee,_=Fee.objects.get_or_create(student=student,title="Semester 1 tuition",academic_year="2026-27",defaults={"total_amount":Decimal("45000.00"),"due_date":date.today()+timedelta(days=30)})
        if not fee.payments.exists(): FeePayment.objects.create(fee=fee,amount=Decimal("15000.00"),reference="DEMO-001",recorded_by=admin_user)
        Notice.objects.get_or_create(title="Welcome to Smart Campus",defaults={"body":"Your campus portal is ready. Check this dashboard regularly for class updates and important dates.","audience":"ALL","author":admin_user})
        TimetableEntry.objects.get_or_create(subject=subject,day=TimetableEntry.Day.MONDAY,start_time=time(9,0),defaults={"end_time":time(10,0),"faculty":faculty,"room":"A-204"})
        self.stdout.write(self.style.SUCCESS("Demo campus is ready."))
        self.stdout.write("Admin: campusadmin / CampusDemo!26")
        self.stdout.write("Faculty: faculty.demo / CampusDemo!26")
        self.stdout.write("Student: student.demo / CampusDemo!26")
        self.stdout.write(self.style.WARNING("Demo credentials are for local evaluation only. Change them before deployment."))
