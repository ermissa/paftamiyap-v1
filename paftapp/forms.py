from django.forms import ModelForm,ModelChoiceField,widgets
from django import forms
from .models import *


class SoftwareChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        exclude = ()
        labels = {
            "name" : "İsminiz",
            "phone_number" : "Telefon Numarası",
            "email" : "Email Adresi"
        }


class ProjectForm(ModelForm):
    softwares = SoftwareChoiceField(
        queryset = Software.objects.all(),
        widget= forms.CheckboxSelectMultiple,
        label = "Projenizde Kullanılacak Yazılımları Seçiniz",
        required=True
    )
    description = forms.CharField(widget=forms.Textarea , label="Projenizi Kısaca Anlatınız")
    field_order = ['customer','softwares','has_render','has_model','map_sheet','deadline','description']
    class Meta:
        model = Project
        exclude = ('customer','clicked_users','is_called','project_status')
        widgets = {
            'deadline': forms.DateInput(format=('%d-%m-%Y'), 
                                             attrs={'type':'date', 
                                            'placeholder':'Select a date'})
        }
        labels = {
            "has_model" : "Maket Yapılacaksa İşaretleyiniz",
            "has_render" : "Render Alınacaksa İşaretleyiniz",
            "map_sheet" : "Pafta Boyutu",
            "deadline" : "Proje Teslim Tarihi",
            "softwares" : "Projenizde Kullanılacak Yazılımları Seçiniz",
            "documentation_path" : "Projenize Ait Dökümantasyon Varsa Yükleyiniz (pdf,png,jpeg veya jpg uzantılı ve maksimum 5MB boyutunda dosya yükleyebilirsiniz.)"
        }



class FeedbackForm(forms.Form):
    name=forms.CharField(label='Name')
    email = forms.EmailField(label="Email Address")
    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={'rows': 5}))