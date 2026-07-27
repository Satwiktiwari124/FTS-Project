from django.urls import path
from . import views


urlpatterns = [
    # HOME
    path('', views.home, name='home'),
    # ADMIN LOGIN
    path('adminlogin/', views.Adminlogin, name='adminlogin'),
    path('loginsave/', views.loginsave, name='loginsave'),
    # ADMIN PANEL
    path('adminlayout/', views.adminlayout, name='adminlayout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    # DEPARTMENT
    path('adddep/', views.adddep, name='adddep'),
    path('depshow/', views.depshow, name='depshow'),
    path('deletedepartment/<int:id>/', views.deletedepartment, name='deletedepartment'),
    # USER
    path('userlogin/', views.user_login, name='userlogin'),
    path('userloginsave/', views.userloginsave, name='userloginsave'),
    path('userlayout/', views.userlayout, name='userlayout'),
    path('userdashboard/', views.userdashboard, name='userdashboard'),
    path('userlogout/', views.userlogout, name='userlogout'),
    # EMPLOYEE
    path('addemployee/', views.addemployee, name='addemployee'),
    path('employeelist/', views.employeelist, name='employeelist'),
    path('deleteemployee/<int:id>/', views.deleteemployee, name='deleteemployee'),
    # FILE
    path('create-file/', views.admin_create_file, name='admin_create_file'),
    path('user/create-file/', views.user_create_file, name='user_create_file'),
    path('ab_file_upload/', views.ab_file_upload, name='ab_file_upload'),
    path('deletefile/<int:id>/', views.deletefile, name='deletefile'),

    path('details/<int:id>/', views.Details_file, name='details_file'),
    path('usershowfile/', views.usershowfile, name='usershowfile'),
    path('receivedfiles/', views.receivedfiles, name='receivedfiles'),
    path('sentfiles/', views.sentfiles, name='sentfiles'),
    path('adminsentfiles/', views.adminsentfiles, name='adminsentfiles'),
    path('adminpendingfiles/', views.adminpendingfiles, name='adminpendingfiles'),
    path('filetrack/', views.filetrack, name='filetrack'),
    path('pendingfiles/', views.pendingfiles, name='pendingfiles'),
    path('admin-details/<int:id>/', views.admin_details_file, name='admin_details_file'),
    path('userfiletrack/', views.userfiletrack, name='userfiletrack'),
    path('editdepartment/<int:id>/', views.editdepartment, name='editdepartment'),
    path('editemployee/<int:id>/', views.editemployee, name='editemployee'),
    
    
    ]