from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Основные маршруты
    path('', views.problem_list, name='problem_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='problem_list'), name='logout'),
    path('problem/create/', views.problem_create, name='problem_create'),
    path('problem/<int:pk>/', views.problem_detail, name='problem_detail'),
    path('problem/<int:pk>/edit/', views.problem_edit, name='problem_edit'),
    path('problem/<int:problem_pk>/accept/<int:solution_pk>/',
         views.accept_solution, name='accept_solution'),

    # Маршруты для управления сотрудниками (только для админа)
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/<int:pk>/toggle-active/', views.employee_toggle_active, name='employee_toggle_active'),
]