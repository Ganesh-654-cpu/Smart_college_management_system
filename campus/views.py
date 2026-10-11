from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import forms
from .models import *

def is_admin(user): return user.is_superuser or user.role == User.Role.ADMIN

def role_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if not (is_admin(request.user) or request.user.role in roles): raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapped
    return decorator

MODULES = {
    "students": ("Students", Student, forms.StudentForm, {"ADMIN"}, "ST"),
    "faculty": ("Faculty", Faculty, forms.FacultyForm, {"ADMIN"}, "FA"),
    "departments": ("Departments", Department, forms.DepartmentForm, {"ADMIN"}, "DE"),
    "courses": ("Courses", Course, forms.CourseForm, {"ADMIN"}, "CO"),
    "subjects": ("Subjects", Subject, forms.SubjectForm, {"ADMIN"}, "SU"),
    "attendance": ("Attendance", Attendance, forms.AttendanceForm, {"ADMIN", "FACULTY"}, "AT"),
    "examinations": ("Examinations", Examination, forms.ExaminationForm, {"ADMIN", "FACULTY"}, "EX"),
    "results": ("Results", Result, forms.ResultForm, {"ADMIN", "FACULTY"}, "RE"),
    "fees": ("Fees", Fee, forms.FeeForm, {"ADMIN"}, "FE"),
    "payments": ("Fee payments", FeePayment, forms.FeePaymentForm, {"ADMIN"}, "PA"),
    "timetable": ("Timetable", TimetableEntry, forms.TimetableForm, {"ADMIN"}, "TI"),
    "notices": ("Notices", Notice, forms.NoticeForm, {"ADMIN", "FACULTY"}, "NO"),
    "materials": ("Study materials", StudyMaterial, forms.StudyMaterialForm, {"ADMIN", "FACULTY"}, "MA"),
}

def login_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard")
    return render(request, "registration/login.html", {"form": form})

@role_required("ADMIN", "FACULTY", "STUDENT")
def dashboard(request):
    user=request.user
    if is_admin(user):
        fee_totals=Fee.objects.aggregate(total=Sum("total_amount"),paid=Sum("paid_amount"))
        context={"student_count":Student.objects.count(),"faculty_count":Faculty.objects.count(),"course_count":Course.objects.count(),
                 "department_count":Department.objects.count(),"recent_notices":Notice.objects.order_by("-published_at")[:5],
                 "attendance_count":Attendance.objects.count(),"pending_fees":(fee_totals["total"] or 0)-(fee_totals["paid"] or 0),
                 "quick_modules":["students","faculty","departments","courses","subjects","attendance","examinations","results","fees","payments","timetable","notices","materials"]}
    elif user.role == User.Role.FACULTY:
        faculty=Faculty.objects.filter(user=user).first()
        subjects=Subject.objects.filter(faculty=faculty) if faculty else Subject.objects.none()
        context={"subjects":subjects,"student_count":Student.objects.filter(course__subjects__in=subjects).distinct().count(),
                 "attendance_count":Attendance.objects.filter(subject__in=subjects).count(),"recent_notices":Notice.objects.filter(Q(audience="ALL")|Q(audience="FACULTY")).order_by("-published_at")[:5],
                 "quick_modules":["subjects","attendance","examinations","results","timetable","notices","materials"]}
    else:
        student=Student.objects.filter(user=user).first()
        context={"student":student,"attendance_count":Attendance.objects.filter(student=student).count() if student else 0,
                 "results":Result.objects.filter(student=student,published=True).select_related("examination","examination__subject") if student else [],
                 "fees":Fee.objects.filter(student=student) if student else [],
                 "timetable_entries":TimetableEntry.objects.filter(subject__course=student.course,subject__semester=student.semester).select_related("subject","faculty__user") if student else [],
                 "recent_notices":Notice.objects.filter(Q(audience="ALL")|Q(audience="STUDENT")).order_by("-published_at")[:5],
                 "materials":StudyMaterial.objects.filter(subject__course=student.course,subject__semester=student.semester) if student else []}
    return render(request,"campus/dashboard.html",context)

def visible_queryset(slug, request):
    title, model, form_class, roles, icon=MODULES[slug]
    qs=model.objects.all()
    user=request.user
    if user.role == User.Role.STUDENT and not is_admin(user):
        student=Student.objects.filter(user=user).first()
        if slug == "students": qs=qs.filter(pk=student.pk) if student else qs.none()
        elif slug == "attendance": qs=qs.filter(student=student) if student else qs.none()
        elif slug == "results": qs=qs.filter(student=student,published=True) if student else qs.none()
        elif slug == "fees": qs=qs.filter(student=student) if student else qs.none()
        elif slug == "timetable" and student: qs=qs.filter(subject__course=student.course,subject__semester=student.semester)
        elif slug == "materials" and student: qs=qs.filter(subject__course=student.course,subject__semester=student.semester)
        elif slug == "notices": qs=qs.filter(Q(audience="ALL")|Q(audience="STUDENT"))
        else: qs=qs.none()
    elif user.role == User.Role.FACULTY and not is_admin(user):
        faculty=Faculty.objects.filter(user=user).first()
        if not faculty: return model.objects.none()
        if slug in ("attendance","examinations","results","materials","timetable","subjects"):
            if slug == "timetable": qs=qs.filter(faculty=faculty)
            elif slug == "results": qs=qs.filter(examination__subject__faculty=faculty)
            else: qs=qs.filter(subject__faculty=faculty)
        elif slug == "notices": qs=qs.filter(Q(audience="ALL")|Q(audience="FACULTY"))
        else: qs=qs.none()
    return qs

@role_required("ADMIN", "FACULTY", "STUDENT")
def module(request, slug, action="list", pk=None):
    if slug not in MODULES: raise PermissionDenied
    title, model, form_class, roles, icon=MODULES[slug]
    user=request.user
    readable_roles=roles | ({"FACULTY"} if slug in {"subjects","timetable"} else set())
    if not is_admin(user) and user.role not in readable_roles:
        # Students have read-only access to their allowed academic views.
        if action != "list" or slug not in {"students","attendance","results","fees","timetable","materials","notices"}: raise PermissionDenied
    qs=visible_queryset(slug,request)
    item=get_object_or_404(qs,pk=pk) if pk is not None else None
    if action == "delete":
        if not is_admin(user): raise PermissionDenied
        if request.method == "POST": item.delete(); messages.success(request,f"{title[:-1] if title.endswith('s') else title} deleted."); return redirect("module",slug=slug)
        return render(request,"campus/confirm_delete.html",{"title":title,"item":item,"slug":slug})
    if action in ("create","edit"):
        if not is_admin(user) and user.role not in roles: raise PermissionDenied
        if request.method == "POST":
            form=form_class(request.POST,request.FILES,instance=item)
            if form.is_valid():
                obj=form.save(commit=False)
                if slug == "payments": obj.recorded_by=user
                if slug == "notices": obj.author=user
                if slug == "materials": obj.uploaded_by=user
                if slug == "attendance" and user.role == User.Role.FACULTY: obj.marked_by=Faculty.objects.filter(user=user).first()
                obj.save(); messages.success(request,f"{title} {'updated' if item else 'created'} successfully."); return redirect("module",slug=slug)
        else: form=form_class(instance=item)
        if not is_admin(user) and user.role == User.Role.FACULTY:
            faculty=Faculty.objects.filter(user=user).first()
            for key in ("subject","examination"):
                if key in form.fields: form.fields[key].queryset=form.fields[key].queryset.filter(faculty=faculty) if key == "subject" else form.fields[key].queryset.filter(subject__faculty=faculty)
            if "marked_by" in form.fields: form.fields["marked_by"].queryset=Faculty.objects.filter(pk=faculty.pk)
        if slug == "attendance" and "student" in form.fields and user.role == User.Role.FACULTY:
            faculty=Faculty.objects.filter(user=user).first(); form.fields["student"].queryset=Student.objects.filter(course__subjects__faculty=faculty).distinct()
        if slug == "results" and "student" in form.fields and user.role == User.Role.FACULTY:
            faculty=Faculty.objects.filter(user=user).first(); form.fields["student"].queryset=Student.objects.filter(course__subjects__faculty=faculty).distinct()
        return render(request,"campus/form.html",{"form":form,"title":title,"item":item,"slug":slug})
    if action != "list": raise PermissionDenied
    search=request.GET.get("q","").strip()
    if search:
        text_fields=[f.name for f in model._meta.fields if isinstance(f,(models.CharField,models.TextField))]
        condition=Q()
        for field in text_fields: condition |= Q(**{f"{field}__icontains":search})
        qs=qs.filter(condition)
    qs=qs.select_related()[:250]
    fields=[f for f in model._meta.fields if f.name not in {"id","password","file"}]
    rows=[]
    for obj in qs:
        values=[]
        for field in fields[:5]:
            value=getattr(obj,field.name)
            values.append((field.verbose_name, value.get_full_name() if isinstance(value,User) else str(value) if value is not None else "—"))
        if slug == "fees": values.extend([("Outstanding balance",str(obj.balance)),("Status",Fee.Status(obj.status).label)])
        elif slug == "results": values.extend([("Percentage",f"{obj.percentage}%"),("Grade",obj.grade)])
        rows.append({"object":obj,"values":values,"download_id":obj.pk if slug == "materials" else None})
    return render(request,"campus/module_list.html",{"title":title,"rows":rows,"slug":slug,"search":search,"can_edit":is_admin(user) or user.role in roles,"is_admin":is_admin(user)})

@require_POST
@role_required("ADMIN")
def quick_notice(request):
    Notice.objects.create(title=request.POST.get("title","Campus update")[:180],body=request.POST.get("body",""),audience=request.POST.get("audience","ALL"),author=request.user)
    messages.success(request,"Notice published.")
    return redirect("dashboard")

@role_required("ADMIN", "FACULTY", "STUDENT")
def download_material(request, pk):
    material=get_object_or_404(visible_queryset("materials",request),pk=pk)
    from django.http import FileResponse
    return FileResponse(material.file.open("rb"),as_attachment=True,filename=material.file.name.split("/")[-1])
