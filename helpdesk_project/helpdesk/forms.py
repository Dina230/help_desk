from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Problem, Solution, Direction


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class EmployeeCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        label="Может создавать/редактировать проблемы",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data['is_staff']

        if commit:
            user.save()
        return user


class ProblemForm(forms.ModelForm):
    files = MultipleFileField(
        required=False,
        label="Прикрепить файлы"
    )

    class Meta:
        model = Problem
        fields = ['title', 'description', 'direction']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 300,
                'placeholder': 'Опишите проблему (макс. 300 символов)'
            }),
            'direction': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание проблемы',
            'direction': 'Направление',
        }


class SolutionForm(forms.ModelForm):
    files = MultipleFileField(
        required=False,
        label="Прикрепить файлы"
    )

    class Meta:
        model = Solution
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'maxlength': 800,
                'placeholder': 'Опишите решение (макс. 800 символов)'
            }),
        }
        labels = {
            'description': 'Описание решения',
        }


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по проблемам...'
        }),
        label=''
    )
    direction = forms.ModelChoiceField(
        queryset=Direction.objects.all(),
        required=False,
        empty_label="Все направления",
        widget=forms.Select(attrs={'class': 'form-control'})
    )