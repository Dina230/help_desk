from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Problem, Direction, Solution, ProblemFile, SolutionFile
from .forms import ProblemForm, SolutionForm, SearchForm, EmployeeCreationForm


# Проверка на администратора
def is_admin(user):
    return user.is_superuser


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('problem_list')
    else:
        form = AuthenticationForm()
    return render(request, 'helpdesk/login.html', {'form': form})


def problem_list(request):
    form = SearchForm(request.GET or None)
    problems = Problem.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        direction = form.cleaned_data.get('direction')

        if query:
            problems = problems.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        if direction:
            problems = problems.filter(direction=direction)

    problems = problems.select_related('author', 'direction').prefetch_related('solutions')

    return render(request, 'helpdesk/problem_list.html', {
        'problems': problems,
        'search_form': form
    })


def problem_detail(request, pk):
    problem = get_object_or_404(
        Problem.objects.prefetch_related(
            'files',
            'solutions__files',
            'solutions__author'
        ),
        pk=pk
    )

    if request.method == 'POST' and request.user.is_authenticated:
        form = SolutionForm(request.POST, request.FILES)
        if form.is_valid():
            solution = form.save(commit=False)
            solution.problem = problem
            solution.author = request.user
            solution.save()

            # Сохраняем файлы
            files = request.FILES.getlist('files')
            for file in files:
                SolutionFile.objects.create(solution=solution, file=file)

            messages.success(request, 'Решение успешно добавлено!')
            return redirect('problem_detail', pk=problem.pk)
    else:
        form = SolutionForm()

    return render(request, 'helpdesk/problem_detail.html', {
        'problem': problem,
        'form': form
    })


@login_required
def problem_create(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.author = request.user
            problem.save()

            # Сохраняем файлы
            files = request.FILES.getlist('files')
            for file in files:
                ProblemFile.objects.create(problem=problem, file=file)

            messages.success(request, 'Проблема успешно создана!')
            return redirect('problem_detail', pk=problem.pk)
    else:
        form = ProblemForm()

    return render(request, 'helpdesk/problem_form.html', {
        'form': form,
        'title': 'Создание проблемы'
    })


@staff_member_required
def problem_edit(request, pk):
    problem = get_object_or_404(Problem, pk=pk)

    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES, instance=problem)
        if form.is_valid():
            problem = form.save()

            # Добавляем новые файлы
            files = request.FILES.getlist('files')
            for file in files:
                ProblemFile.objects.create(problem=problem, file=file)

            messages.success(request, 'Проблема успешно обновлена!')
            return redirect('problem_detail', pk=problem.pk)
    else:
        form = ProblemForm(instance=problem)

    return render(request, 'helpdesk/problem_form.html', {
        'form': form,
        'title': 'Редактирование проблемы'
    })


@login_required
def accept_solution(request, problem_pk, solution_pk):
    problem = get_object_or_404(Problem, pk=problem_pk)

    # Проверяем, что пользователь является автором проблемы
    if request.user == problem.author:
        solution = get_object_or_404(Solution, pk=solution_pk, problem=problem)

        # Снимаем отметку с предыдущего принятого решения
        Solution.objects.filter(problem=problem, is_accepted=True).update(is_accepted=False)

        # Отмечаем новое решение как принятое
        solution.is_accepted = True
        solution.save()

        messages.success(request, 'Решение отмечено как принятое!')

    return redirect('problem_detail', pk=problem_pk)


# Административные функции для управления сотрудниками
@user_passes_test(is_admin)
def employee_list(request):
    employees = User.objects.all().order_by('-date_joined')
    return render(request, 'helpdesk/employee_list.html', {
        'employees': employees
    })


@user_passes_test(is_admin)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Сотрудник {user.username} успешно создан!')
            return redirect('employee_list')
    else:
        form = EmployeeCreationForm()

    return render(request, 'helpdesk/employee_form.html', {
        'form': form,
        'title': 'Создание сотрудника'
    })


@user_passes_test(is_admin)
def employee_edit(request, pk):
    employee = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST, instance=employee)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Данные сотрудника {user.username} обновлены!')
            return redirect('employee_list')
    else:
        # Создаем форму с текущими данными пользователя
        form = EmployeeCreationForm(instance=employee)
        # Заполняем дополнительные поля
        form.fields['email'].initial = employee.email
        form.fields['first_name'].initial = employee.first_name
        form.fields['last_name'].initial = employee.last_name
        form.fields['is_staff'].initial = employee.is_staff

    return render(request, 'helpdesk/employee_form.html', {
        'form': form,
        'title': f'Редактирование сотрудника: {employee.username}'
    })


@user_passes_test(is_admin)
def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk)

    # Не даем удалить самого себя
    if request.user == employee:
        messages.error(request, 'Вы не можете удалить свою учетную запись!')
        return redirect('employee_list')

    if request.method == 'POST':
        username = employee.username
        employee.delete()
        messages.success(request, f'Сотрудник {username} удален!')
        return redirect('employee_list')

    return render(request, 'helpdesk/employee_confirm_delete.html', {
        'employee': employee
    })


@user_passes_test(is_admin)
def employee_toggle_active(request, pk):
    employee = get_object_or_404(User, pk=pk)

    # Не даем деактивировать самого себя
    if request.user == employee:
        messages.error(request, 'Вы не можете деактивировать свою учетную запись!')
        return redirect('employee_list')

    employee.is_active = not employee.is_active
    employee.save()

    status = "активирован" if employee.is_active else "деактивирован"
    messages.success(request, f'Сотрудник {employee.username} {status}!')

    return redirect('employee_list')