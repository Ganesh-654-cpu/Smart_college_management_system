from django import forms
from .models import Attendance, Course, Department, Examination, Faculty, Fee, FeePayment, Notice, Result, Student, StudyMaterial, Subject, TimetableEntry

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (field.widget.attrs.get("class", "") + " form-control").strip()

class DepartmentForm(StyledModelForm):
    class Meta: model=Department; fields="__all__"
class CourseForm(StyledModelForm):
    class Meta: model=Course; fields="__all__"
class FacultyForm(StyledModelForm):
    class Meta: model=Faculty; fields="__all__"
class StudentForm(StyledModelForm):
    class Meta: model=Student; fields="__all__"
class SubjectForm(StyledModelForm):
    class Meta: model=Subject; fields="__all__"
class AttendanceForm(StyledModelForm):
    class Meta: model=Attendance; fields="__all__"
class ExaminationForm(StyledModelForm):
    class Meta: model=Examination; fields="__all__"
class ResultForm(StyledModelForm):
    class Meta: model=Result; fields="__all__"
    def clean(self):
        data=super().clean()
        if data.get("examination") and data.get("marks") is not None and data["marks"] > data["examination"].max_marks:
            self.add_error("marks", "Marks cannot exceed the examination maximum.")
        return data
class FeeForm(StyledModelForm):
    class Meta: model=Fee; fields="__all__"
class FeePaymentForm(StyledModelForm):
    class Meta: model=FeePayment; fields=("fee", "amount", "paid_on", "reference")
    def clean_amount(self):
        amount=self.cleaned_data["amount"]
        fee=self.cleaned_data.get("fee")
        if fee and amount > fee.balance: raise forms.ValidationError("Payment cannot exceed the outstanding balance.")
        return amount
class TimetableForm(StyledModelForm):
    class Meta: model=TimetableEntry; fields="__all__"
    def clean(self):
        data=super().clean()
        if data.get("start_time") and data.get("end_time") and data["end_time"] <= data["start_time"]:
            self.add_error("end_time", "End time must be later than start time.")
        return data
class NoticeForm(StyledModelForm):
    class Meta: model=Notice; fields=("title", "body", "audience")
class StudyMaterialForm(StyledModelForm):
    class Meta: model=StudyMaterial; fields=("subject", "title", "description", "file")
