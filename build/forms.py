from django import forms
from django.contrib.auth.models import User
from .chocolate import replace_all

from lxml import etree
import urllib2, urllib
import datetime

from .models import *
from context.models import *
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
#
#                                           FORMS
#
#    The following forms are mostly associated with models.  The first form, ConfirmForm, is an example 
# of a form that is not associated with any models.  The specification for the PDS4 components 
# (ex: Alias, Bundle, ...) can be found in models.py with the corresponding model object.  The comments
# for the following forms should include the input format rules.  This information may or may not need
# to be in models over forms.  I'm not too sure where we will decide to do our data checking as of yet.
# Some models listed below that have choices do include the specification as a part of data checking.
#
# TASK:  Add data checking/cleaning to fit ELSA standard.
#
# ------------------------------------------------------------------------------------------------------ #


"""
    Confirm
"""
class ConfirmForm(forms.Form):
    CHOICES = [('Yes','Yes') , ('No','No')]
    decision = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())


"""
    Alias
"""
class AliasForm(forms.ModelForm):

    class Meta:
        model = Alias
        exclude = ('bundle',)












"""
    Bundle
"""
class BundleForm(forms.ModelForm):
    name = forms.CharField( initial='Enter name here', required=True, max_length=50) 
    version = forms.ModelChoiceField(queryset=Version.objects.all(), required=True, help_text="Version")

    class Meta:
        model = Bundle              
        fields = ('name', 'bundle_type', 'version', )


    """
        clean should ensure the following:
            - The name of the bundle can fit within a given lid length
                - Unfortunately, not enough data has been collected for us to have a good boundary  
                  idea.  A lid must be no more than 255 characters (double check).
            - The name should be ready for lid case. <-- I feel like this should be removed now that
              there is a model that puts name into lid case.  The cleaner should be a minimal 
              cleansing of data.
            - The user should not append bundle to the end of the bundle name.
    """
    def clean(self):                                     # name_edit can be removed from this function
        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')

        # - The name of the bundle should be less than or equal to 255 characters

        if len(name) <= 255:
            name_edit = name
            name_edit = name_edit.lower()
            name_edit = replace_all(name_edit, ' ', '_') # replace spaces with underscores
            if name_edit.endswith("bundle"):
                name_edit = name_edit[:-7] # seven because there is probably an underscore by now
            if name_edit.find(':') != -1:
                raise forms.ValidationError("The colon (:) is used to delimit segments of a urn and thus is not permitted within a bundle name.")
        else:
            raise forms.ValidationError("The length of your bundle name is too large");














"""
    Citation_Information
"""
class CitationInformationForm(forms.ModelForm):

    description = forms.CharField(required=True)
    publication_year = forms.DateField(required=True, input_formats=['%Y'])

    class Meta:
        model = Citation_Information
        exclude = ('bundle',)


    """
        clean should do nothing to the description.  For publication_year, CitationInformationForm uses Django's DateField form field.  Django's DateField form field (https://docs.djangoproject.com/en/2.0/_modules/django/forms/fields/#DateField) simply sees if the input could be converted to a date time object.  Therefore, values like 6020 can be input.  We need to decide if we want to prevent user errors such as this, raise warnings to the user, do nothing, etc...
    """
    def clean(self):
        pass










"""
    Collections
"""
class CollectionsForm(forms.ModelForm):
    has_document = forms.BooleanField(required=True, initial=True)
    has_context = forms.BooleanField(required=True, initial=True)
    has_xml_schema = forms.BooleanField(required=True, initial=True)

    class Meta:
        model = Collections
        exclude = ('bundle',)











"""
    Data
"""
class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        exclude = ('bundle', 'collection')











"""
    Investigation
"""
class InvestigationForm(forms.Form):
    investigation = forms.ModelChoiceField(queryset=Investigation.objects.all(), required=True, help_text="Note: Investigations can be individual, missions, observing campaigns, or other</br>")

class InstrumentHostForm(forms.Form):

    instrument_host = forms.ModelChoiceField(queryset = Instrument_Host.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        self.pk_inv = kwargs.pop('pk_inv')
        super(InstrumentHostForm,self).__init__(*args, **kwargs)
        self.fields['instrument_host'] = forms.ModelChoiceField(queryset=Instrument_Host.objects.filter(investigation=self.pk_inv), required=True)

######### HERE : https://medium.com/@MicroPyramid/understanding-djangos-model-fromsets-in-detail-and-their-advanced-usage-131dfe66853d

"""
    Product_Bundle
"""
class ProductBundleForm(forms.ModelForm):

    class Meta:
        model = Product_Bundle
        exclude = ('bundle',)














"""
    Product_Collection
"""
class ProductCollectionForm(forms.ModelForm):

    class Meta:
        model = Product_Collection
        exclude = ('collection', 'collections',)











"""
12.1  Document                               k: Product_Document

Root Class:Tagged_NonDigital_Object
Role:Concrete

Class Description:The Document class describes a document.

Steward:pds
Namespace Id:pds
Version Id:2.0.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Tagged_NonDigital_Object	 	 	 
        	. TNDO_Supplemental	 	 	 
 	        . . Document	 	 	 

Subclass	none	 	 	 

Attribute
	acknowledgement_text	0..1	 	 
 	author_list     	0..1	 	 
 	copyright       	0..1	 	 
 	description	        0..1	 	 
 	document_editions	0..1	 	 
 	document_name	        0..1  An exec decision has been made to make document_name required
 	doi	                0..1	 	 
 	editor_list	        0..1	 	 
 	publication_date	1	 	 
 	revision_id	        0..1	 	 

Inherited Attribute	none	 	 	 
Association	        data_object	        1	Digital_Object	 
 	                has_document_edition	1..*	Document_Edition	 
Inherited Association	none	 	 	 
Referenced from	Product_Document	 	 	 
"""
class ProductDocumentForm(forms.ModelForm):
    document_name = forms.CharField(required=True)
    publication_date = forms.CharField(required=True)
    acknowledgement_text = forms.CharField(required=False)
    author_list = forms.CharField(required=False)
    copyright = forms.CharField(required=False)
    description = forms.CharField(required=False)
    document_editions = forms.CharField(required=False)
    doi = forms.CharField(required=False)
    editor_list = forms.CharField(required=False)
    revision_id = forms.CharField(required=False)

    class Meta:
        model = Product_Document
        exclude = ('bundle',)













"""
    Product_Observational
"""
class ProductObservationalForm(forms.ModelForm):
    OBSERVATIONAL_TYPES = [

        ('Table Binary','Table Binary'),
        ('Table Character','Table Character'),
        ('Table Delimited','Table Delimited'),
    ]
    PURPOSE_TYPES = [
        ('Calibration','Calibration'),
        ('Checkout','Checkout'),
        ('Engineering','Engineering'),
        ('Navigation','Navigation'),
        ('Observation Geometry','Observation Geometry'),
        ('Science','Science'),
    ]
    purpose = forms.ChoiceField(required=True, choices=PURPOSE_TYPES)
    title = forms.CharField(required=True)
    type_of = forms.ChoiceField(required=True, choices=OBSERVATIONAL_TYPES)

    class Meta:
        model = Product_Observational
        exclude = ('bundle', 'data', 'processing_level')













"""
    Table
"""
class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        exclude = ('product_observational', 'observational_type', 'local_identifier')



