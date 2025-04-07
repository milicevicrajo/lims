from django_select2.forms import Select2Widget, Select2MultipleWidget

def select2_widget(attrs=None):
    if attrs is None:
        attrs = {'class': 'select2-method'}
    return Select2Widget(attrs=attrs)

def select2_multiple_widget(attrs=None):
    if attrs is None:
        attrs = {'class': 'select2-method'}
    return Select2MultipleWidget(attrs=attrs)
