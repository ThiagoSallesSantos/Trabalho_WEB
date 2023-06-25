from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from .models import *


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class MontarSorvete(forms.Form):
    sorvete = forms.HiddenInput()
    tigela = forms.RadioSelect()
    componentes = forms.CheckboxSelectMultiple()

    class Meta:
        model = Produto
        fields = ['componentes', 'tigela', 'sorvete'] 

class ComprarSorvete(forms.Form):
	id_produto = forms.MultipleHiddenInput()
	precos_produto = forms.MultipleHiddenInput()
	qtd_sorvete = forms.NumberInput()
	preco = forms.HiddenInput()

	class Meta:
		model = Venda
		fields = ['produtos']