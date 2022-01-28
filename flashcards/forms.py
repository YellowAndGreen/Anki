from django import forms


class SearchForm(forms.Form):
    query = forms.CharField()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class CreateForm(forms.Form):
    query2 = forms.CharField()
