from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        FACULTY = "FACULTY", "Faculty"
        STUDENT = "STUDENT", "Student"
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN: self.is_staff = True
        super().save(*args, **kwargs)
    def has_perm(self, perm, obj=None):
        if self.is_active and self.role == self.Role.ADMIN: return True
        return super().has_perm(perm,obj)
    def has_module_perms(self, app_label):
        if self.is_active and self.role == self.Role.ADMIN: return True
        return super().has_module_perms(app_label)
    def __str__(self): return self.get_full_name() or self.username

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=12, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return f"{self.name} ({self.code})"

class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="courses")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    duration_years = models.PositiveSmallIntegerField(default=3)
    def __str__(self): return self.name

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="faculty")
    qualification = models.CharField(max_length=120, blank=True)
    employee_id = models.CharField(max_length=24, unique=True)
    def __str__(self): return f"{self.employee_id} - {self.user}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="students")
    roll_number = models.CharField(max_length=24, unique=True)
    enrollment_number = models.CharField(max_length=32, unique=True)
    semester = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(12)])
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    admission_date = models.DateField(default=timezone.localdate)
    @property
    def attendance_percentage(self):
        rows=self.attendance_records.all()
        total=rows.count()
        attended=rows.filter(status__in=[Attendance.Status.PRESENT,Attendance.Status.LATE]).count() if total else 0
        return round(attended * 100 / total, 1) if total else 0
    def __str__(self): return f"{self.roll_number} - {self.user}"

class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=24, unique=True)
    semester = models.PositiveSmallIntegerField(default=1)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name="subjects")
    class Meta: ordering = ["course__name", "semester", "name"]
    def __str__(self): return f"{self.code} · {self.name}"

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "subject", "date"], name="one_attendance_per_day")]
        ordering = ["-date"]
    def __str__(self): return f"{self.student} · {self.subject} · {self.date}"

class Examination(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="examinations")
    exam_date = models.DateField()
    max_marks = models.PositiveSmallIntegerField(default=100)
    class Meta: ordering = ["-exam_date"]
    def __str__(self): return f"{self.name} · {self.subject}"

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name="results")
    marks = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    published = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "examination"], name="one_result_per_exam")]
    @property
    def percentage(self): return round(float(self.marks) * 100 / self.examination.max_marks, 1) if self.examination.max_marks else 0
    @property
    def grade(self):
        p = self.percentage
        return "A+" if p >= 90 else "A" if p >= 80 else "B" if p >= 70 else "C" if p >= 60 else "D" if p >= 40 else "F"
    def __str__(self): return f"{self.student} · {self.examination}"

class Fee(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PARTIAL = "PARTIAL", "Partially paid"
        PAID = "PAID", "Paid"
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    title = models.CharField(max_length=100, default="Tuition fee")
    academic_year = models.CharField(max_length=12, default="2026-27")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    due_date = models.DateField(null=True, blank=True)
    @property
    def balance(self): return max(self.total_amount - self.paid_amount, 0)
    @property
    def status(self): return Fee.Status.PAID if self.balance == 0 else Fee.Status.PARTIAL if self.paid_amount > 0 else Fee.Status.PENDING
    def __str__(self): return f"{self.student} · {self.title}"

class FeePayment(models.Model):
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    paid_on = models.DateField(default=timezone.localdate)
    reference = models.CharField(max_length=40, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def save(self, *args, **kwargs):
        old_fee_id = FeePayment.objects.filter(pk=self.pk).values_list("fee_id",flat=True).first() if self.pk else None
        super().save(*args, **kwargs)
        self.refresh_fee_total(self.fee_id)
        if old_fee_id and old_fee_id != self.fee_id: self.refresh_fee_total(old_fee_id)
    @staticmethod
    def refresh_fee_total(fee_id):
        fee=Fee.objects.filter(pk=fee_id).first()
        if fee:
            fee.paid_amount=min(fee.total_amount,fee.payments.aggregate(s=models.Sum("amount"))["s"] or 0)
            fee.save(update_fields=["paid_amount"])
    def delete(self, *args, **kwargs):
        fee_id=self.fee_id
        result=super().delete(*args,**kwargs)
        self.refresh_fee_total(fee_id)
        return result
    def __str__(self): return f"{self.fee} · {self.amount}"

class TimetableEntry(models.Model):
    class Day(models.TextChoices):
        MONDAY="MON", "Monday"; TUESDAY="TUE", "Tuesday"; WEDNESDAY="WED", "Wednesday"; THURSDAY="THU", "Thursday"; FRIDAY="FRI", "Friday"; SATURDAY="SAT", "Saturday"
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="timetable_entries")
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="timetable_entries")
    day = models.CharField(max_length=3, choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=32)
    class Meta: ordering = ["day", "start_time"]
    def clean(self):
        super().clean()
        if not self.day or not self.start_time or not self.end_time: return
        overlaps=TimetableEntry.objects.filter(day=self.day,start_time__lt=self.end_time,end_time__gt=self.start_time)
        if self.pk: overlaps=overlaps.exclude(pk=self.pk)
        if overlaps.filter(Q(faculty=self.faculty)|Q(room__iexact=self.room)).exists():
            raise ValidationError("The faculty member or classroom already has a timetable entry in this time slot.")
    def __str__(self): return f"{self.get_day_display()} · {self.subject} · {self.start_time}"

class Notice(models.Model):
    title = models.CharField(max_length=180)
    body = models.TextField()
    audience = models.CharField(max_length=12, choices=[("ALL","Everyone"),("STUDENT","Students"),("FACULTY","Faculty")], default="ALL")
    published_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self): return self.title

class StudyMaterial(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="study_materials/%Y/%m/", validators=[FileExtensionValidator(["pdf", "doc", "docx", "ppt", "pptx", "txt"])])
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    def __str__(self): return self.title
