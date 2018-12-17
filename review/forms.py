from django import forms




# A normal form with questions and answers for the user.  These questions and answers were pulled from Danae's version of ELSA.
class ReviewForm(forms.Form):

    reviewer = forms.CharField(label='Name of person who reviewed your data:')
    derived_data = forms.CharField(required=True, label='Name of derived data set reviewed:')
    CHOICES = ( ('PDS3', 'PDS3'), ('PDS4', 'PDS4'), )
    archive_standard = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    question1 = forms.CharField(widget=forms.Textarea, label='Do the derived data provide clear and concise documentation adequate for its usage?')
    question2 = forms.CharField(widget=forms.Textarea, label='Are you able to manipulate and plot the data, interpret columns into tables, and understand the context and relationships of the data products?')
    question3 = forms.CharField(widget=forms.Textarea, label='Are there any concerns about the creation/generation, calibration, or general usability of the data?')
    question4 = forms.CharField(widget=forms.Textarea, label='Any further comments to PDS Atmospheres Node about the data?')
