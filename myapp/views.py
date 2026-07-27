from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .models import addemployee as Employee
from django.db.models import Q
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django.conf import settings
from django.http import FileResponse, Http404
import os
# HOME

def home(request):
    return render(request, 'user/home.htm')

# ADMIN LOGIN

def Adminlogin(request):
    return render(request, 'admin/adminlogin.htm')

def loginsave(request):
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = adminlogin.objects.filter(
            username=username,
            password=password
        ).first()

        if user:
            request.session['adminid'] = user.id
            request.session['adminusername'] = user.username

            return redirect('dashboard')

        messages.error(
            request,
            'Invalid Username or Password'
        )

        return redirect('adminlogin')

    return redirect('adminlogin')
# ADMIN LAYOUT

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminlayout(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    return render(
        request,
        'admin/adminlayout.htm'
    )
# ADMIN DASHBOARD

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    total_files = Fileupload.objects.count()
    pending_files = Fileupload.objects.filter(status='Pending').count()
    total_employees = Employee.objects.count()
    total_departments = adddepartment.objects.count()

    recent_files = Fileupload.objects.all().order_by('-created_at')[:5]

    return render(
        request,
        'admin/dashboard.htm',
        {
            'total_files': total_files,
            'pending_files': pending_files,
            'total_employees': total_employees,
            'total_departments': total_departments,
            'recent_files': recent_files
        }
    )

# ADMIN LOGOUT
def logout(request):
    request.session.flush()

    return redirect('adminlogin')

# USER LOGIN

def user_login(request):
    return render(
        request,
        'user/userlogin.htm'
    )
# USER LOGIN SAVE

def userloginsave(request):
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = userlogin.objects.filter(
            username=username,
            password=password
        ).first()

        if user:
            request.session['user_id'] = user.id
            request.session['username'] = user.username

            return redirect('userdashboard')

        messages.error(
            request,
            'Invalid Username or Password'
        )

        return redirect('userlogin')

    return redirect('userlogin')

# USER LAYOUT

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlayout(request):
    if 'user_id' not in request.session:
        return redirect('userlogin')

    return render(
        request,
        'user/userlayout.htm'
    )
    
# USER DASHBOARD

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userdashboard(request):
    if 'user_id' not in request.session:
        return redirect('userlogin')

    username = request.session.get('username')

    my_files_count = Fileupload.objects.filter(
        Q(create_user=username) | Q(current_user=username)
    ).distinct().count()

    received_count = Fileupload.objects.filter(current_user=username).count()

    sent_count = Fileupload.objects.filter(create_user=username).count()

    pending_count = Fileupload.objects.filter(
        current_user=username,
        status='Pending'
    ).count()

    recent_files = Fileupload.objects.filter(
        Q(create_user=username) | Q(current_user=username)
    ).order_by('-created_at')[:5]

    recent_movement = []

    for f in recent_files:

        if f.create_user == username and f.current_user != username:
            action = "Created & Forwarded"
        elif f.current_user == username:
            action = f.status
        else:
            action = f.status

        recent_movement.append({
            'file_no': f.file_no,
            'subject': f.subject,
            'from_user': f.create_user,
            'to_user': f.current_user,
            'action': action,
            'created_at': f.created_at,
        })

    return render(
        request,
        'user/userdashboard.htm',
        {
            'username': username,
            'my_files_count': my_files_count,
            'received_count': received_count,
            'sent_count': sent_count,
            'pending_count': pending_count,
            'recent_movement': recent_movement,
        }
    )

# SERVE FILE (LOGIN PROTECTED)
# NEVER link {{ data.file.url }} directly in templates - that bypasses
# login entirely since MEDIA_URL has no auth check. Always link to this
# view instead: {% url 'serve_file' data.id %}

def serve_file(request, id):

    if 'user_id' not in request.session and 'adminid' not in request.session:
        return redirect('userlogin')

    filedata = get_object_or_404(Fileupload, id=id)

    if not filedata.file:
        raise Http404("No file attached to this record")

    file_path = filedata.file.path

    if not os.path.exists(file_path):
        raise Http404("File not found on server")

    return FileResponse(
        open(file_path, 'rb'),
        filename=os.path.basename(file_path)
    )

# USER LOGOUT

def userlogout(request):
    request.session.flush()

    return redirect('userlogin')

# ADD EMPLOYEE
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addemployee(request):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    if request.method == "POST":

        name = request.POST.get('name')
        emailaddress = request.POST.get('email')
        password = request.POST.get('password')

        Employee.objects.create(
            name=name,
            username=request.POST.get('username'),
            email=emailaddress,
            mobile=request.POST.get('mobile'),
            empid=request.POST.get('empid'),
            department=request.POST.get('department'),
            designation=request.POST.get('designation'),
            role=request.POST.get('role'),
            status=request.POST.get('status'),
            password=password,
            photo=request.FILES.get('photo'),
            address=request.POST.get('address')
        )

        # Also create a userlogin entry so the employee can log in
        if not userlogin.objects.filter(username=request.POST.get('username')).exists():
            userlogin.objects.create(
                username=request.POST.get('username'),
                email=emailaddress,
                password=password
            )

        message = f"""
Dear {name},

Greetings from Green Gas Limited (GGL).

Your account has been successfully created for the GGL File Tracking System.

You can log in using the following credentials:
--------------------------------------------------------
User ID / Email : {emailaddress}
Password        : {password}
--------------------------------------------------------

Login Instructions:
1. Open the GGL File Tracking System.
2. Enter your User ID and Password.
3. Change your password after your first login (if applicable).
4. Start managing and tracking your assigned files.

Important:
* Keep your login credentials confidential.
* Do not share your password with anyone.
* If you forget your password or face any login issues, please contact the System Administrator.

Thank you for using the GGL File Tracking System.

Regards,
System Administrator
GGL File Tracking System
Green Gas Limited (GGL)
"""

        send_mail(
            "GGL File Tracking System - Login Credentials",
            message,
            settings.EMAIL_HOST_USER,
            [emailaddress],
            fail_silently=False
        )

        messages.success(
            request,
            "Employee Added Successfully"
        )

        return redirect('employeelist')

    departmentdata = adddepartment.objects.all()

    return render(
        request,
        'admin/addemployee.htm',
        {
            'department': departmentdata
        }
    )

# EMPLOYEE LIST
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employeelist(request):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    employeedata = Employee.objects.all()

    return render(
        request,
        'admin/employeelist.htm',
        {
            'employeedata': employeedata
        }
    )

# DELETE EMPLOYEE

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteemployee(request, id):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    employee = Employee.objects.get(id=id)
    employee.delete()

    messages.success(
        request,
        "Employee Deleted Successfully"
    )

    return redirect('employeelist')
# FILE LIST

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ab_file_upload(request):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    filedata = Fileupload.objects.all()

    return render(
        request,
        'admin/trackfile.htm',
        {
            'filedata': filedata
        }
    )

# DELETE FILE
def deletefile(request, id):

    # Only admin can delete files
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    data = Fileupload.objects.get(id=id)
    data.delete()

    messages.success(
        request,
        'File Deleted Successfully'
    )

    # Redirect based on referer
    referer = request.META.get('HTTP_REFERER', '')

    if 'pendingfiles' in referer:
        return redirect('adminpendingfiles')
    return redirect('ab_file_upload')
# DEPARTMENT (without edit)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adddep(request):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    if request.method == "POST":
        department_name = request.POST.get('department_name')
        department_code = request.POST.get('department_code')
        department_head = request.POST.get('department_head')
        status = request.POST.get('status')
        department_email = request.POST.get('department_email')
        contact_number = request.POST.get('contact_number')

        adddepartment.objects.create(
            department_name=department_name,
            department_code=department_code,
            dep_head=department_head,
            status=status,
            dep_email=department_email,
            dep_number=contact_number
        )

        messages.success(request, "Department Added Successfully")

        # Save hone ke baad list page par jayega
        return redirect('depshow')

    return render(request, 'admin/adddep.htm')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def depshow(request):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    depdata = adddepartment.objects.all()

    return render(
        request,
        'admin/depshow.htm',
        {'depdata': depdata}
    )

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deletedepartment(request, id):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    department = adddepartment.objects.get(id=id)
    department.delete()

    messages.success(request, "Department Deleted Successfully")

    return redirect('depshow')
# FILE DETAILS
def Details_file(request, id):

    if 'user_id' not in request.session and 'adminid' not in request.session:
        return redirect('userlogin')

    ab = Fileupload.objects.get(id=id)
    track_history = FileMovement.objects.filter(file=ab).order_by('-moved_at')
    users = userlogin.objects.all()

    if request.method == "POST":

        action = request.POST.get('action')
        forward_to = request.POST.get('forward_to')
        remark = request.POST.get('remark')
        current_username = request.session.get('username')
        # Only update current_user and create movement record if forwarding
        if action == 'Forwarded':
            FileMovement.objects.create(
                file=ab,
                from_user=current_username,
                to_user=forward_to,
                action=action,
                remarks=remark
            )
            ab.current_user = forward_to
            ab.status = 'Pending'
        else:
            FileMovement.objects.create(
                file=ab,
                from_user=current_username,
                to_user=ab.current_user,
                action=action,
                remarks=remark
            )
            ab.status = action

        ab.save()

        messages.success(request, "File Moved Successfully")

        return redirect('details_file', id=id)

    return render(
        request,
        'user/detailes.htm',
        {
            'ab': ab,
            'track_history': track_history,
            'users': users
        }
    )
# ADMIN FILE DETAILS
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_details_file(request, id):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    ab = Fileupload.objects.get(id=id)
    track_history = FileMovement.objects.filter(file=ab).order_by('-moved_at')
    users = userlogin.objects.all()

    if request.method == "POST":

        action = request.POST.get('action')
        forward_to = request.POST.get('forward_to')
        remark = request.POST.get('remark')
        current_username = request.session.get('adminusername')

        # Only update current_user and create movement record if forwarding
        if action == 'Forwarded':
            FileMovement.objects.create(
                file=ab,
                from_user=current_username,
                to_user=forward_to,
                action=action,
                remarks=remark
            )
            ab.current_user = forward_to
            ab.status = 'Pending'
        else:
            FileMovement.objects.create(
                file=ab,
                from_user=current_username,
                to_user=ab.current_user,
                action=action,
                remarks=remark
            )
            ab.status = action

        ab.save()

        messages.success(request, "File Moved Successfully")

        return redirect('admin_details_file', id=id)

    return render(
        request,
        'admin/detailsfile.htm',
        {
            'ab': ab,
            'track_history': track_history,
            'users': users
        }
    )
# USER CREATE FILE
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_create_file(request):

    if 'user_id' not in request.session:
        return redirect('userlogin')

    if request.method == "POST":

        file_no = request.POST.get('file_no')

        if Fileupload.objects.filter(file_no=file_no).exists():
            messages.error(request, "This File No already exists")
            return redirect('user_create_file')

        Fileupload.objects.create(
            file_no=file_no,
            subject=request.POST.get('subject'),
            priority=request.POST.get('priority'),
            create_user=request.session.get('username'),
            departments=request.POST.get('department'),
            current_user=request.POST.get('employee'),
            file=request.FILES.get('attachment'),
            description=request.POST.get('description'),
            remarks=request.POST.get('remarks'),
            status='Pending'
        )

        messages.success(request, "File Created Successfully")
        return redirect('userdashboard')

    users = userlogin.objects.all()
    return render(request, 'user/uploadfile.htm', {'users': users})
# ADMIN CREATE FILE
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_create_file(request):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    if request.method == "POST":

        file_no = request.POST.get('file_no')

        if Fileupload.objects.filter(file_no=file_no).exists():
            messages.error(request, "This File No already exists")
            return redirect('admin_create_file')

        Fileupload.objects.create(
            file_no=file_no,
            subject=request.POST.get('subject'),
            priority=request.POST.get('priority'),
            create_user=request.session.get('adminusername'),
            departments=request.POST.get('department'),
            current_user=request.POST.get('employee'),
            file=request.FILES.get('attachment'),
            description=request.POST.get('description'),
            remarks=request.POST.get('remarks'),
            status='Pending'
        )

        messages.success(request, "File Created Successfully")
        return redirect('ab_file_upload')

    users = userlogin.objects.all()
    return render(request, 'admin/createfile.htm', {'users': users})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def usershowfile(request):
    if 'user_id' not in request.session:
        return redirect('userlogin')

    filedata = Fileupload.objects.all()

    return render(
        request,
        'user/usershowfile.htm',
        {
            'filedata': filedata
        }
    )

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def receivedfiles(request):
    if 'user_id' not in request.session:
        return redirect('userlogin')

    username = request.session.get('username')

    filedata = Fileupload.objects.filter(current_user=username)

    return render(
        request,
        'user/receivedfiles.htm',
        {
            'filedata': filedata
        }
    )

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sentfiles(request):
    if 'user_id' not in request.session:
        return redirect('userlogin')

    username = request.session.get('username')

    # Only show files that have been acted upon (forwarded/approved/
    # rejected/completed) at least once. Freshly-created files still
    # untouched by anyone should not appear as "Sent".
    filedata = Fileupload.objects.filter(create_user=username).filter(
        Q(status__in=['Approved', 'Rejected', 'Completed']) |
        Q(filemovement__isnull=False)
    ).distinct()

    return render(
        request,
        'user/sentfiles.htm',
        {
            'filedata': filedata
        }
    )

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminsentfiles(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    username = request.session.get('adminusername')

    # Same rule as user sentfiles: hide untouched, still-pending files.
    filedata = Fileupload.objects.filter(create_user=username).filter(
        Q(status__in=['Approved', 'Rejected', 'Completed']) |
        Q(filemovement__isnull=False)
    ).distinct()

    return render(
        request,
        'admin/sentfiles.htm',
        {
            'filedata': filedata
        }
    )

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminpendingfiles(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    filedata = Fileupload.objects.filter(status='Pending')

    return render(
        request,
        'admin/pendingfiles.htm',
        {
            'filedata': filedata
        }
    )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def filetrack(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    query = request.GET.get('query', '').strip()
    filedata = None

    if query:
        filedata = Fileupload.objects.filter(
            Q(file_no__icontains=query) |
            Q(subject__icontains=query) |
            Q(create_user__icontains=query) |
            Q(current_user__icontains=query)
        )

    return render(
        request,
        'admin/filetrack.htm',
        {
            'filedata': filedata,
            'query': query
        }
    )
# USER PENDING FILES
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pendingfiles(request):
    if 'user_id' not in request.session:
        return redirect('userlogin')

    username = request.session.get('username')

    filedata = Fileupload.objects.filter(
        current_user=username,
        status='Pending'
    )

    return render(
        request,
        'user/pendingfiles.htm',
        {
            'filedata': filedata
        }
    )
# USER FILE TRACK
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userfiletrack(request):
    if 'user_id' not in request.session:
        return redirect('userlogin')

    username = request.session.get('username')
    query = request.GET.get('query', '').strip()
    filedata = None

    if query:
        filedata = Fileupload.objects.filter(
            Q(file_no__icontains=query) |
            Q(subject__icontains=query) |
            Q(create_user__icontains=query) |
            Q(current_user__icontains=query)
        ).filter(
            Q(create_user=username) | Q(current_user=username)
        )

    return render(
        request,
        'user/filetrack.htm',
        {
            'filedata': filedata,
            'query': query
        }
    )
# EDIT DEPARTMENT
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editdepartment(request, id):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    department = get_object_or_404(adddepartment, id=id)

    if request.method == "POST":

        department.department_name = request.POST.get('department_name')
        department.department_code = request.POST.get('department_code')
        department.dep_head = request.POST.get('department_head')
        department.status = request.POST.get('status')
        department.dep_email = request.POST.get('department_email')
        department.dep_number = request.POST.get('contact_number')
        department.save()

        messages.success(request, "Department Updated Successfully")
        return redirect('depshow')

    return render(
        request,
        'admin/editdepartment.htm',
        {'department': department}
    )
# EDIT EMPLOYEE
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editemployee(request, id):

    if 'adminid' not in request.session:
        return redirect('adminlogin')

    employee = get_object_or_404(Employee, id=id)

    if request.method == "POST":

        employee.name = request.POST.get('name')
        employee.username = request.POST.get('username')
        employee.email = request.POST.get('email')
        employee.mobile = request.POST.get('mobile')
        employee.empid = request.POST.get('empid')
        employee.department = request.POST.get('department')
        employee.designation = request.POST.get('designation')
        employee.role = request.POST.get('role')
        employee.status = request.POST.get('status')

        password = request.POST.get('password')
        if password:
            employee.password = password

        if request.FILES.get('photo'):
            employee.photo = request.FILES.get('photo')

        employee.save()

        messages.success(request, "Employee Updated Successfully")
        return redirect('employeelist')

    departmentdata = adddepartment.objects.all()

    return render(
        request,
        'admin/editemployee.htm',
        {
            'employee': employee,
            'department': departmentdata
        }
    )