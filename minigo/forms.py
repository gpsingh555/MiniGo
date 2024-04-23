from django import forms


class SignupForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
 
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    
class CampaignStepOneForm(forms.Form):
    campaign_type = forms.CharField(required=True)
    campaign_name = forms.CharField(required=True)
    promotion_goal = forms.CharField(required=True)
    secondary_goal = forms.CharField(required=False)
    re_target = forms.CharField(required=False)
    csv_gaid = forms.FileField(label='Gaid CSV', required=False)