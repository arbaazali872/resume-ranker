from django import forms

class JobDescriptionForm(forms.Form):
    job_description = forms.FileField(
        label='Upload Job Description', 
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx,.txt'})
    )

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'class': 'form-control-file'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ResumeForm(forms.Form):
    files = MultipleFileField()
