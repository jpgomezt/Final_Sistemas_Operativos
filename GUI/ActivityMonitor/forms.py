from django import forms

class FolderForm(forms.Form):
    folder_name = forms.CharField(max_length=20)