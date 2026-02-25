from django.contrib import admin
from django.utils.html import format_html
from .models import Direction, Problem, ProblemFile, Solution, SolutionFile


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'problems_count', 'created_problems', 'status_badge']
    list_filter = ['name']
    search_fields = ['name', 'display_name']
    ordering = ['name']
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'display_name'),
            'description': 'Выберите код направления и укажите отображаемое название'
        }),
    )

    def problems_count(self, obj):
        count = obj.problems.count()
        url = f"/admin/helpdesk/problem/?direction__id__exact={obj.id}"
        return format_html(
            '<a href="{}" class="button" style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">{} проблем(ы)</a>',
            url, count)

    problems_count.short_description = 'Количество проблем'
    problems_count.allow_tags = True

    def created_problems(self, obj):
        recent_problems = obj.problems.order_by('-created_at')[:5]
        if recent_problems:
            html = '<ul style="margin: 0; padding-left: 20px;">'
            for problem in recent_problems:
                html += f'<li><a href="/admin/helpdesk/problem/{problem.id}/change/">{problem.title}</a> <small>({problem.created_at | date:"d.m.Y"})</small></li>'
            html += '</ul>'
            return format_html(html)
        return format_html('<span style="color: #999;">Нет проблем</span>')

    created_problems.short_description = 'Последние проблемы'

    def status_badge(self, obj):
        if obj.problems.exists():
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Активно</span>')
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Не активно</span>')

    status_badge.short_description = 'Статус'

    actions = ['duplicate_direction', 'clear_problems']

    def duplicate_direction(self, request, queryset):
        for direction in queryset:
            direction.pk = None
            direction.name = f"{direction.name}_copy"
            direction.display_name = f"{direction.display_name} (копия)"
            direction.save()
        self.message_user(request, f"Создано {queryset.count()} копий направлений")

    duplicate_direction.short_description = "Создать копию выбранных направлений"

    def clear_problems(self, request, queryset):
        for direction in queryset:
            count = direction.problems.count()
            direction.problems.all().delete()
            self.message_user(request, f"Удалено {count} проблем из направления {direction.display_name}")

    clear_problems.short_description = "Удалить все проблемы в выбранных направлениях"

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


class ProblemFileInline(admin.TabularInline):
    model = ProblemFile
    extra = 1
    fields = ['file', 'file_preview', 'uploaded_at']
    readonly_fields = ['file_preview', 'uploaded_at']

    def file_preview(self, obj):
        if obj.file:
            file_ext = obj.file.name.split('.')[-1].lower()
            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 3px;" />',
                                   obj.file.url)
            else:
                return format_html(
                    '<span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 3px;">📎 {}</span>',
                    file_ext.upper())
        return "Нет файла"

    file_preview.short_description = 'Предпросмотр'


class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 0
    fields = ['description_short', 'author', 'created_at', 'is_accepted', 'files_count']
    readonly_fields = ['description_short', 'author', 'created_at', 'files_count']

    def description_short(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description

    description_short.short_description = 'Описание'

    def files_count(self, obj):
        count = obj.files.count()
        return format_html(
            '<span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 10px;">{}</span>', count)

    files_count.short_description = 'Файлов'


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'direction', 'author', 'created_at', 'solutions_count', 'has_files', 'status_badge']
    list_filter = ['direction', 'created_at', 'author']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['author', 'created_at', 'updated_at', 'solutions_list']
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'direction'),
            'classes': ('wide',)
        }),
        ('Автор и даты', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Решения', {
            'fields': ('solutions_list',),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProblemFileInline, SolutionInline]

    def solutions_count(self, obj):
        count = obj.solutions.count()
        accepted = obj.solutions.filter(is_accepted=True).count()
        if accepted > 0:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">{} ✅</span>',
                count)
        return format_html(
            '<span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">{}</span>', count)

    solutions_count.short_description = 'Решения'

    def has_files(self, obj):
        count = obj.files.count()
        if count > 0:
            return format_html(
                '<span style="background: #17a2b8; color: white; padding: 3px 8px; border-radius: 3px;">📎 {}</span>',
                count)
        return format_html('<span style="color: #999;">Нет</span>')

    has_files.short_description = 'Файлы'

    def status_badge(self, obj):
        if obj.solutions.filter(is_accepted=True).exists():
            return format_html(
                '<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 3px;">Решено</span>')
        elif obj.solutions.exists():
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 5px 10px; border-radius: 3px;">В работе</span>')
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 5px 10px; border-radius: 3px;">Нет решений</span>')

    status_badge.short_description = 'Статус'

    def solutions_list(self, obj):
        solutions = obj.solutions.all()
        if not solutions:
            return "Нет решений"

        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #f8f9fa;"><th>Автор</th><th>Описание</th><th>Дата</th><th>Статус</th></tr>'
        for solution in solutions:
            bg_color = '#d4edda' if solution.is_accepted else 'transparent'
            html += f'<tr style="background: {bg_color};">'
            html += f'<td style="padding: 5px; border: 1px solid #dee2e6;">{solution.author}</td>'
            html += f'<td style="padding: 5px; border: 1px solid #dee2e6;">{solution.description[:100]}...</td>'
            html += f'<td style="padding: 5px; border: 1px solid #dee2e6;">{solution.created_at | date:"d.m.Y H:i"}</td>'
            html += f'<td style="padding: 5px; border: 1px solid #dee2e6;">{"✅ Принято" if solution.is_accepted else "⏳ Ожидает"}</td>'
            html += '</tr>'
        html += '</table>'
        return format_html(html)

    solutions_list.short_description = 'Список решений'

    actions = ['mark_as_solved', 'mark_as_unsolved', 'delete_solutions']

    def mark_as_solved(self, request, queryset):
        for problem in queryset:
            if problem.solutions.exists():
                # Отмечаем первое решение как принятое
                first_solution = problem.solutions.first()
                problem.solutions.update(is_accepted=False)
                first_solution.is_accepted = True
                first_solution.save()
        self.message_user(request, f"Отмечено {queryset.count()} проблем как решенные")

    mark_as_solved.short_description = "Отметить как решенные (первым решением)"

    def mark_as_unsolved(self, request, queryset):
        for problem in queryset:
            problem.solutions.update(is_accepted=False)
        self.message_user(request, f"Отмечено {queryset.count()} проблем как нерешенные")

    mark_as_unsolved.short_description = "Снять отметку о решении"

    def delete_solutions(self, request, queryset):
        total = 0
        for problem in queryset:
            count = problem.solutions.count()
            total += count
            problem.solutions.all().delete()
        self.message_user(request, f"Удалено {total} решений")

    delete_solutions.short_description = "Удалить все решения выбранных проблем"

    def save_model(self, request, obj, form, change):
        if not change:  # Если создается новая запись
            obj.author = request.user
        super().save_model(request, obj, form, change)


class SolutionFileInline(admin.TabularInline):
    model = SolutionFile
    extra = 1
    fields = ['file', 'file_preview', 'uploaded_at']
    readonly_fields = ['file_preview', 'uploaded_at']

    def file_preview(self, obj):
        if obj.file:
            file_ext = obj.file.name.split('.')[-1].lower()
            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 3px;" />',
                                   obj.file.url)
            else:
                return format_html(
                    '<span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 3px;">📎 {}</span>',
                    file_ext.upper())
        return "Нет файла"

    file_preview.short_description = 'Предпросмотр'


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ['problem_link', 'author', 'created_at', 'is_accepted', 'files_count']
    list_filter = ['is_accepted', 'created_at', 'author']
    search_fields = ['description', 'problem__title', 'author__username']
    readonly_fields = ['author', 'created_at']
    list_per_page = 25
    inlines = [SolutionFileInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('problem', 'description'),
            'classes': ('wide',)
        }),
        ('Автор и статус', {
            'fields': ('author', 'created_at', 'is_accepted'),
        }),
    )

    def problem_link(self, obj):
        return format_html('<a href="/admin/helpdesk/problem/{}/change/">{}</a>',
                           obj.problem.id, obj.problem.title)

    problem_link.short_description = 'Проблема'

    def files_count(self, obj):
        count = obj.files.count()
        return format_html(
            '<span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 10px;">📎 {}</span>',
            count)

    files_count.short_description = 'Файлы'

    actions = ['accept_solutions', 'unaccept_solutions']

    def accept_solutions(self, request, queryset):
        for solution in queryset:
            # Снимаем отметку с других решений этой проблемы
            solution.problem.solutions.exclude(id=solution.id).update(is_accepted=False)
            solution.is_accepted = True
            solution.save()
        self.message_user(request, f"Отмечено {queryset.count()} решений как принятые")

    accept_solutions.short_description = "Отметить как принятые решения"

    def unaccept_solutions(self, request, queryset):
        queryset.update(is_accepted=False)
        self.message_user(request, f"Снята отметка с {queryset.count()} решений")

    unaccept_solutions.short_description = "Снять отметку о принятии"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)
