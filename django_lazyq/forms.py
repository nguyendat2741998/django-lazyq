from django import forms


class RequestFormValidate(forms.Form):
    model = forms.ChoiceField(choices=())

    def __init__(self, models_cls, *args, **kwargs):
        super(RequestFormValidate, self).__init__(*args, **kwargs)
        self.fields['model'].choices = list([(k, k) for k in models_cls.keys])
