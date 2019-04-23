# Stdlib imports
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from shutil import copyfile
from .chocolate import *
from context.models import *
import datetime
import shutil
import os








#    Final Variables ------------------------------------------------------------------------------------
MAX_CHAR_FIELD = 100
MAX_LID_FIELD = 255
MAX_TEXT_FIELD = 1000

PDS4_LABEL_TEMPLATE_DIRECTORY = os.path.join(settings.TEMPLATE_DIR, 'pds4_labels')


#       --- These will be changed when Version model object gets complete ---
MODEL_LOCATION = "http://pds.nasa.gov/pds4/schema/released/pds/v1/PDS4_PDS_1800.sch"
NAMESPACE = "{http://pds.nasa.gov/pds4/pds/v1}"
SCHEMA_INSTANCE = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_LOCATION = "http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/schema/released/pds/v1/PDS4_PDS_1800.xsd"











#    Helpful functions here ----------------------------------------------------------------------------
"""
"""
def get_most_current_version():
    # Get all versions listed in ELSA
    Version_List = Version.objects.all()

    if Version_List:
        # Find the highest version number

        highest_number = 0

        for version in Version_List:
            if version.num > highest_number:
                highest_number = version.num
                highest_version = version

            # Now that we have iterated through the list, the highest number should be obtained
            return highest_version
    else:
        return 0


"""
"""
def get_upload_path(instance, filename):
    return '{0}/{1}'.format(instance.user.id, filename)





"""
"""
def get_three_years_in_future():
    now = datetime.datetime.now()
    return now.year + 3




"""
"""
def get_user_document_directory(instance, filename):
    document_collection_directory = 'archive/{0}/{1}/documents/'.format(instance.bundle.user.username, instance.bundle.name)
    return document_collection_directory



#    Register your models here -----------------------------------------------------------------------

"""
    Note:  Most names in ELSA are explicit.  However, we could not make a 'number' attribute to identify the version number (ex: 1800, 1A00, 1A10) because it conflicted with Django's number attribute given to each model.
"""
@python_2_unicode_compatible
class Version(models.Model):

    num = models.CharField(max_length=4)
    xml_model = models.CharField(max_length=MAX_CHAR_FIELD)
    xmlns = models.CharField(max_length=MAX_CHAR_FIELD)
    xsi = models.CharField(max_length=MAX_CHAR_FIELD)
    schemaLocation = models.CharField(max_length=MAX_CHAR_FIELD)
    schematypens = models.CharField(max_length=MAX_CHAR_FIELD)

    """
         __str__ returns a string to be displayed when a model object is called.
         For the Version model object we want a four-digit value like 1800 or 1A00.
    """
    def __str__(self):
        return self.num

    """
        with_dots gives the version num with dots between each number.  Sometimes in PDS4
        we require that the number include dots, other times not so much.  For four-digit values with
        hex characters (1A00), we should return the hex character as its decimal equivalent (1.10.0.0).
    """
    def with_dots(self):
        version_number = self.num
        new_number = ''

        # Add a period after each digit.  Ex: 1234 -> 1.2.3.4.
        for each_digit in version_number:
            new_number = '{0}{1}{2}'.format(new_number, each_digit, '.')

        # Remove the last period. Ex: 1.2.3.4. -> 1.2.3.4
        new_number = new_number[:-1]

        # Number is now formatted to pds standard, so return it.
        return new_number

    """
        fill_xml_schema takes in the root of a label (ex tags: Product_Bundle, Product_Collection)
        and adds in the xml-model processing instruction and the xsi:schemaLocation

    
        Fillers follow a set flow.
            1. Input the root element of an XML label.
                - We want the root because we can access all areas of the document through it's root.
            2. Find the areas you want to fill.
                - Always do find over a static search to ensure we are always on the right element.
                  (  ex. of static search ->    root[0] = Identification_Area in fill_base_case    )
                  Originally, ELSA used a static search for faster performance, but we found out
                  that comments in the XML label through the code off and we were pulling incorrect
                  elements.
            3. Fill those areas.
                - Fill is easy.  Just fill it.. with the information from the model it was called on,
                  self (like itself).
    
    """
    def fill_xml_schema(self, root):

        # Change the xml-model processing instruction
        text = 'href={0} schematypens="http://purl.oclc.org/dsdl/schematron"'.format(self.xml_model)
        root.addprevious(etree.ProcessingInstruction('xml-model', text=text))

        # Change the xsi:schemaLocation

        return root

    def validate(self):
        print 'Currently, ELSA does no version validation.'


    # Validators
    def get_validators(self):
        pass





"""
"""
@python_2_unicode_compatible
class Bundle(models.Model):
    """
    Bundle has a many-one correspondance with User so a User can have multiple Bundles.
    Bundle name is currently not unique and we may want to ask someone whether or not it should be.
    If we require Bundle name to be unique, we could implement a get_or_create so multiple users
    can work on the same Bundle.  However we first must figure out how to click a Bundle and have it
    display the Build-A-Bundle app with form data pre-filled.  Not too sure how to go about this.
    """

    BUNDLE_STATUS = (
        ('b', 'Build'),
        ('r', 'Review'),
        ('s', 'Submit'),
    )
    BUNDLE_TYPE_CHOICES = (
        ('Archive', 'Archive'),
        ('Supplemental', 'Supplemental'),
    )

    bundle_type = models.CharField(max_length=12, choices=BUNDLE_TYPE_CHOICES, default='Archive',)
    name = models.CharField(max_length=MAX_CHAR_FIELD, unique=True)
    status = models.CharField(max_length=1, choices=BUNDLE_STATUS, blank=False, default='b')     
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    # To implement where the default is the most current version, we first need to grab all versions
    # and then grab the one with the highest number.

    # Context Attributes
    investigations = models.ManyToManyField(Investigation)
    instrument_hosts = models.ManyToManyField(Instrument_Host)
    instruments = models.ManyToManyField(Instrument)
    targets = models.ManyToManyField(Target)


    


    def __str__(self):
        return self.name



    """
    - absolute_url
      Returns the url to the Bundle Detail page.
    """
    def absolute_url(self):
        return reverse('build:bundle', args=[str(self.id)])



    """
    """
    def directory(self):
        bundle_directory = os.path.join(settings.ARCHIVE_DIR, self.user.username)
        bundle_directory = os.path.join(bundle_directory, self.name_directory_case())
        return bundle_directory



    """
    - name_title_case
      Returns the bundle name in normal Title case with spaces.
    """
    def name_title_case(self):          
        name_edit = self.name
        name_edit = replace_all(name_edit, '_', ' ')
        return name_edit.title()



    """
    - name_directory_case
      Returns the bundle name in PDS4 compliant directory case with spaces.
      This is lid case with '_bundle' at the end.
    """
    def name_directory_case(self):

        # self.name is in title case with spaces
        name_edit = self.name

        # edit name to be in lower case        
        name_edit = name_edit.lower()

        # edit name to have underscores where spaces are present
        name_edit = replace_all(name_edit, ' ', '_')

        # edit name to append _bundle at the end
        name_edit = '{0}_bundle'.format(name_edit)

        return name_edit


    """
    """
    def name_file_case(self):

        # Get bundle name in directory case: {name_of_bundle}_bundle
        name_edit = self.name_directory_case()

        # Remove _bundle
        name_edit = name_edit[:-7]

        # Now we are returning {name_of_bundle} where {name_of_bundle} is lowercase with underscores rather than spaces
        return name_edit

    """
    name_lid_case
         - Returns the name in proper lid case.
             - Maximum Length: 255 characters
             - Allowed characters: lower case letters, digits, dash, period, underscore
             - Delimiters are colons (So no delimiters in name).
    """
    def name_lid_case(self):
        return self.name_file_case()

    def lid(self):
        return 'urn:{0}:{1}'.format(self.user.userprofile.agency, self.name_lid_case())



    """ 
        build_directory currently is not working.
    """
    def build_directory(self):
        user_path = os.path.join(settings.ARCHIVE_DIR, self.user.username)
        print user_path
        bundle_path = os.path.join(user_path, self.name_directory_case())
        make_directory(bundle_path)
        self.save()




    """
        remove_bundle removes the bundle directory and all of its contents from the user's directory.  If 
        the directory was removed, then the bundle model object is deleted from the ELSA database.  The 
        function then returns status true if everything was removed correctly.

    """
    def remove_bundle(self):
        # Declarations    
        debug_status = True
        complete_removal_status = False
        directory_removal_status = False
        model_removal_status = False

    
        if debug_status == True:
            print '-----------------------------'
            print 'remove_bundle \n\n'
            print 'bundle_directory: {}'.format(self.directory())

        if os.path.isdir(self.directory()):

            if debug_status == True:
                print 'os.path.isdir(self.directory()): True'

            shutil.rmtree(self.directory())
            if not os.path.isdir(self.directory()):
                directory_removal_status = True

        if Bundle.objects.filter(name=self.name, user=self.user).count() > 0: # Should be no more than one
            b = Bundle.objects.filter(name=self.name, user=self.user)
            b.delete()
            if Bundle.objects.filter(name=self.name, user=self.user).count() == 0:
                model_removal_status = True

        if directory_removal_status and model_removal_status:
            complete_removal_status = True
            

        return complete_removal_status


    """
       update is used when a new label is being created for a product. Given a product, update will see which objects (whether that be other products or individual components of a label like an alias) are currently associated with the bundle and ensure all of the current metadata will be found on the new label being created for the given product.
    """
    def update(self, product):

        # Components of labels
        alias_set = Alias.objects.filter(bundle=self)
        citation_information_set = Alias.objects.filter(bundle=self)
        # context_set = Needs to be created still
        # modification_history_set --> Needs to be created still

        # Products
        document_set = Document.objects.filter(bundle=self)
        data_set = Data.objects.filter(data=self)

        print alias_set
        print citation_information_set
        print document_set
        print data_set








"""
"""
@python_2_unicode_compatible
class Collections(models.Model):


    # Attributes
    bundle = models.OneToOneField(Bundle, on_delete=models.CASCADE)
    has_document = models.BooleanField(default=True)
    has_context = models.BooleanField(default=True)
    has_xml_schema = models.BooleanField(default=True)
    has_data = models.BooleanField(default=False)
    has_browse = models.BooleanField(default=False)
    has_calibration = models.BooleanField(default=False)
    has_geometry = models.BooleanField(default=False)


    # Cleaners
    def list(self):
        collections_list = []
        if self.has_document:
            collections_list.append("document")
        if self.has_context:
            collections_list.append("context")
        if self.has_xml_schema:
            collections_list.append("xml_schema")
        if self.has_data:
            collections_list.append("data")
        if self.has_browse:
            collections_list.append("browse")
        if self.has_calibration:
            collections_list.append("calibration")
        if self.has_geometry:
            collections_list.append("geometry")
        return collections_list



    #     Note: When we call on Collections, we want to be able to have a list of all collections 
    #           pertaining to a bundle.
    def __str__(self):
        return '{0} Bundle has document={1}, context={2}, xml_schema={3}, data={4}, browse={5}, calibrated={6}, geometry={7}'.format(self.bundle, self.has_document, self.has_context, self.has_xml_schema, self.has_data, self.has_browse, self.has_calibration, self.has_geometry)
    class Meta:
        verbose_name_plural = 'Collections'        


    def build_directories(self):
        for collection in self.list():
            #collection_directory = os.path.join(self.bundle.directory(), collection)
            #make_directory(collection_directory)

            if collection != "data":
                collection_directory = os.path.join(self.bundle.directory(), collection)
                make_directory(collection_directory)
                # We don't want the data collection to make a folder titled data.  Instead, the data 
                # collection is a set of folders where the name(s) of these folders take on the form 
                # data_<processing_level>.  For example: data_raw, data_calibrated, etc.  When a 
                # user adds in a data product, we find out what type of data they have.  At this 
                # point, ELSA will build the data_<processing_level> folder if it does not already 
                # exist. The model object that creates the data collection folders is the Data model 
                # object.



















"""
15.1  Product_Bundle

Root Class:Product
Role:Concrete

Class Description:A Product_Bundle is an aggregate product and has a table of references to one or more collections.

Steward:pds
Namespace Id:pds

Version Id:1.1.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product	 	 	 
        	. Product_Bundle	 	 	 

Subclass	        none	 	 	 
Attribute	        none	 	 	 
Inherited Attribute	none	 	 	 
Association	        context_area	        0..1	Context_Area	 
                 	file_area	        0..1	File_Area_Text	 
                	member_entry	        1..*	Bundle_Member_Entry	 
                 	product_data_object	1	Bundle	 
                	reference_list	        0..1	Reference_List	 
Inherited Association	has_identification_area	1	Identification_Area	 
Referenced from	none	 	 	 
"""
@python_2_unicode_compatible
class Product_Bundle(models.Model):
    bundle = models.OneToOneField(Bundle, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: Product Bundle'.format(self.bundle)
    

    def name_file_case(self):
        # Append bundle name in file case to name edit for a Product_Bundle xml label
        name_edit = 'bundle_{}.xml'.format(self.bundle.name_file_case())
        return name_edit

    
    """
        label gives the physical location of the label on atmos (or wherever).  Since Product_Bundle is located within the bundle directory, our path is .../user_directory_here/bundle_directory_here/product_bundle_label_here.xml.
    """
    def label(self):
        return os.path.join(self.bundle.directory(), self.name_file_case())


    """
        build_base_case copies the base case product_bundle template (versionless) into bundle dir
    """
    def build_base_case(self):

        
        # Locate base case Product_Bundle template found in templates/pds4_labels/base_case/product_bundle
        source_file = os.path.join(settings.TEMPLATE_DIR, 'pds4_labels')
        source_file = os.path.join(source_file, 'base_case')
        source_file = os.path.join(source_file, 'product_bundle.xml')

        # Copy the base case template to the correct directory
        copyfile(source_file, self.label())
        
        return
        
    """
        fill_base_case is the initial fill given the bundle name, version, and collections.


        Fillers follow a set flow.
            1. Input the root element of an XML label.
                - We want the root because we can access all areas of the document through it's root.
            2. Find the areas you want to fill.
                - Always do find over a static search to ensure we are always on the right element.
                  (  ex. of static search ->    root[0] = Identification_Area in fill_base_case    )
                  Originally, ELSA used a static search for faster performance, but we found out
                  that comments in the XML label through the code off and we were pulling incorrect
                  elements.
            3. Fill those areas.
                - Fill is easy.  Just fill it.. with the information from the model it was called on,
                  self (like itself).
    
    """
    def fill_base_case(self, root):
        Product_Bundle = root
 
        # Fill in Identification_Area
        Identification_Area = Product_Bundle.find('{}Identification_Area'.format(NAMESPACE))

        #     lid
        logical_identifier = Identification_Area.find('{}logical_identifier'.format(NAMESPACE))
        logical_identifier.text = self.bundle.lid()
        

        #     version_id --> Note:  Can be changed to be more dynamic once we implement bundle versions (which is different from PDS4 versions)
        version_id = Identification_Area.find('{}version_id'.format(NAMESPACE))
        version_id.text = '1.0'  

        #     title
        title = Identification_Area.find('{}title'.format(NAMESPACE))
        title.text = self.bundle.name_title_case()

        #     information_model_version
        #information_model_version = Identification_Area.find('{}information_model_version'.format(NAMESPACE))
        #information_model_version = self.bundle.version.name_with_dots()
        
        return Product_Bundle

    """
        build_internal_reference builds and fills the Internal_Reference information within the 
        Reference_List of Product_Bundle.  The relation is used within reference_type to associate what 
        the bundle is related to, like bundle_to_document.  Therefore, relation is a model object in 
        ELSA, like Document.  The possible relations as of V1A00 are errata, document, investigation, 
        instrument, instrument_host, target, resource, associate.
    """
    def build_internal_reference(self, root, relation):

        Reference_List = root.find('{}Reference_List'.format(NAMESPACE))

        Internal_Reference = etree.SubElement(Reference_List, 'Internal_Reference')

        lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
        lid_reference.text = relation.lid()

        reference_type = etree.SubElement(Internal_Reference, 'reference_type')
        reference_type.text = 'bundle_to_{}'.format(relation.reference_type())   

        return root   


    def base_case(self):
        return








"""
15.2  Product_Collection

Root Class:Product
Role:Concrete


Class Description:A Product_Collection has a table of references to one or more basic products. The references are stored in a table called the inventory.


Steward:pds
Namespace Id:pds
Version Id:1.1.0.0
  	Entity 	Card 	Value/Class 	Ind


Hierarchy	Product	 	 	 
         	. Product_Collection	 	 	 


Subclass	        none	 	 	 
Attribute	        none	 	 	 
Inherited Attribute	none	 	 	 


Association	context_area	        0..1	Context_Area	 
        	file_area_inventory	1	File_Area_Inventory	 
        	product_data_object	1	Collection	 
 	        reference_list	        0..1	Reference_List	 


Inherited Association	has_identification_area	1	Identification_Area	 


Referenced from	none	 	 	 
"""
@python_2_unicode_compatible
class Product_Collection(models.Model):
    COLLECTION_CHOICES = (

        ('Document','Document'),
        ('Context','Context'),
        ('XML_Schema','XML_Schema'),
        ('Data_Calibrated','Data_Calibrated'),
        ('Data_Derived', 'Data_Derived'),
        ('Data_Raw','Data_Raw'),
        ('Data_Reduced','Data_Reduced'),
        ('Browse','Browse'),
        ('Geometry','Geometry'),
        ('Calibration','Calibration'),


    )
#   bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    collections = models.ForeignKey(Collections, on_delete=models.CASCADE) #Could be wise to delete.
    collection = models.CharField(max_length=MAX_CHAR_FIELD, choices=COLLECTION_CHOICES, default='Not_Set')


    def __str__(self):
        
        return "{0}\nProduct Collection for {1} Collection".format(self.collections.bundle, self.collection)
    

    """
        This returns the directory path of all collections but the data collection.
        To return any of the data collection directory paths, see directory_data.
    """
    def directory(self):
        name_edit = self.collection.lower()
        collection_directory = os.path.join(self.collections.bundle.directory(), name_edit)
        return collection_directory

    """
        Note that directory_data requires a data object to be passed to find the directory path.
        This is because the data collection path has the processing level in its name.  ELSA waits
        until the user submits data to create all things data related, including these names.
        From demos of ELSA, the simplicity of the first step seems to really attract people.
        Because of this, I (k) have decided to wait until a user is ready to input information
        about their data before asking questions about their data.  Due to this, the data collection 
        is a special case.  Later down the road, you may find this was a bad idea.  Alas, other
        collections such as Browse, Calibration, etc., have yet to be touched.
    """
    def directory_data(self, data):
        name_edit = 'data_{1}'.format(self.collection.lower(), data.processing_level.lower())
        collection_directory = os.path.join(self.collections.bundle.directory(), name_edit)
        return collection_directory

    """
       name_label_case returns the name in label case with the proper .xml extension.
    """        
    def name_label_case(self):

        # Append cleaned collection name to name edit for Product_Collection xml label
        name_edit = self.collection.lower()
        name_edit = 'collection_{}.xml'.format(name_edit)
        return name_edit

    def name_label_case_data(self, data):
        # Append cleaned collection name to name edit for Product_Collection xml label
        name_edit = 'collection_{}.xml'.format(self.collection.lower())
        return name_edit

    """
       label returns the physical label location in ELSAs archive
    """
    def label(self):
        return os.path.join(self.directory(), self.name_label_case())

    def label_data(self, data):
        return os.path.join(data.directory(), self.name_label_case())


    """
    """
    def build_base_case(self):
        
        # Locate base case Product_Collection template found in templates/pds4_labels/base_case/
        source_file = os.path.join(PDS4_LABEL_TEMPLATE_DIRECTORY, 'base_case')
        source_file = os.path.join(source_file, 'product_collection.xml')

        # Locate collection directory and create path for new label
        label_file = os.path.join(self.directory(), self.name_label_case())


        # Copy the base case template to the correct directory
        copyfile(source_file, label_file)
            
        return

    def build_base_case_data(self, data):
        
        # Locate base case Product_Collection template found in templates/pds4_labels/base_case/
        source_file = os.path.join(PDS4_LABEL_TEMPLATE_DIRECTORY, 'base_case')
        source_file = os.path.join(source_file, 'product_collection.xml')

        # Locate collection directory and create path for new label
        label_file = os.path.join(self.directory_data(data), self.name_label_case_data(data))


        # Copy the base case template to the correct directory if it does not already exist
        if not os.path.exists(label_file):
            copyfile(source_file, label_file)
            
        return


    """
        Fillers follow a set flow.
            1. Input the root element of an XML label.
                - We want the root because we can access all areas of the document through it's root.
            2. Find the areas you want to fill.
                - Always do find over a static search to ensure we are always on the right element.
                  (  ex. of static search ->    root[0] = Identification_Area in fill_base_case    )
                  Originally, ELSA used a static search for faster performance, but we found out
                  that comments in the XML label through the code off and we were pulling incorrect
                  elements.
            3. Fill those areas.
                - Fill is easy.  Just fill it.. with the information from the model it was called on,
                  self (like itself).
    """
    def fill_base_case(self, root):
        Product_Collection = root
         
        # Fill in Identification_Area
        Identification_Area = Product_Collection.find('{}Identification_Area'.format(NAMESPACE))

        #     lid
        logical_identifier = Identification_Area.find('{}logical_identifier'.format(NAMESPACE))
        logical_identifier.text = 'urn:{0}:{1}:{2}'.format(self.collections.bundle.user.userprofile.agency, self.collections.bundle.name_lid_case(), self.collection) # where agency is something like nasa:pds
        

        #     version_id --> Note:  Can be changed to be more dynamic once we implement bundle versions (which is different from PDS4 versions)
        version_id = Identification_Area.find('{}version_id'.format(NAMESPACE))
        version_id.text = '1.0'  

        #     title
        title = Identification_Area.find('{}title'.format(NAMESPACE))
        title.text = self.collections.bundle.name_title_case()

        #     information_model_version
        #information_model_version = Identification_Area.find('{}information_model_version'.format(NAMESPACE))
        #information_model_version = self.bundle.version.name_with_dots()
        
        return Product_Collection

    """
        build_internal_reference builds and fills the Internal_Reference information within the Reference_List of Product_Collection.  The relation is used within reference_type to associate what the collection is related to, like collection_to_document.  Therefore, relation is a model object in ELSA, like Document.  The possible relations as of V1A00 are resource, associate, calibration, geometry, spice kernel, document, browse, context, data, ancillary, schema, errata, bundle, personnel, investigation, instrument, instrument_host, target.
    """

    def build_internal_reference(self, root, relation):

        Reference_List = root.find('{}Reference_List'.format(NAMESPACE))

        Internal_Reference = etree.SubElement(Reference_List, 'Internal_Reference')

        lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
        lid_reference.text = relation.lid()

        reference_type = etree.SubElement(Internal_Reference, 'reference_type')
        reference_type.text = 'collection_to_{}'.format(relation.reference_type())   

        return root   








"""
"""
@python_2_unicode_compatible
class Data(models.Model):
    PROCESSING_LEVEL_CHOICES = (            
        ('Calibrated', 'Calibrated'),
        ('Derived', 'Derived'),
        ('Raw', 'Raw'),
        ('Reduced', 'Reduced'),
    )
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    processing_level = models.CharField(max_length=30, choices=PROCESSING_LEVEL_CHOICES,)
    collection = models.ForeignKey(Product_Collection, on_delete=models.CASCADE)


    class Meta:
        verbose_name_plural = 'Data'    


    def __str__(self):
        return 'Data associated'  # Better this once we work on data more


    # build_directory builds a directory of the form data_<processing_level>.  
    # Function make_directory(path) can be found in chocolate.py.  It checks the existence
    # of a directory before creating the directory.
    def build_directory(self):
        data_directory = os.path.join(self.bundle.directory(),'data_{}'.format(self.processing_level.lower()))
        make_directory(data_directory)


    # directory returns the file path associated with the given model.
    def directory(self):
        data_collection_name = 'data_{}'.format(self.processing_level.lower())
        data_directory = os.path.join(self.bundle.directory(), data_collection_name)
        return data_directory  


    """
       label returns the physical label location in ELSAs archive
    """
    def label(self):
        return os.path.join(self.directory(), self.collection.name_label_case())
    """


    """



















"""
8.3  Product_Observational

Root Class:Product
Role:Concrete

Class Description:A Product_Observational is a set of one or more information objects produced by an observing system.

Steward:pds
Namespace Id:pds
Version Id:1.7.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product	 	 	 
         	. Product_Observational	 	 	 

Subclass	        none	 	 	 
Attribute	        none	 	 	 
Inherited Attribute	none	 	 	 
Association	file_area       	1..*	File_Area_Observational	 
        	file_area_supplemental	0..*	File_Area_Observational_Supplemental	 
 	        observation_area	1	Observation_Area	 
        	reference_list	        0..1	Reference_List	 

Inherited Association	has_identification_area	1	Identification_Area	 

Referenced from	none	 	 	 
"""
@python_2_unicode_compatible
class Product_Observational(models.Model):
    DOMAIN_TYPES = [
        ('Atmosphere','Atmosphere'),
        ('Dynamics','Dynamics'),
        ('Heliosphere','Heliosphere'),
        ('Interior','Interior'),
        ('Interstellar','Interstellar'),
        ('Ionosphere','Ionosphere'),
        ('Magnetosphere','Magnetosphere'),
        ('Rings','Rings'),
        ('Surface','Surface'),
    ]
    DISCIPLINE_TYPES = [
        ('Atmospheres','Atmospheres'),
        ('Fields','Fields'),
        ('Flux Measurements','Flux Measurements'),
        ('Geosciences','Geosciences'),
        ('Imaging','Imaging'),
        ('Particles','Particles'),
        ('Radio Science','Radio Science'),
        ('Ring-Moon Systems','Ring-Moon Systems'),
        ('Small Bodies','Small Bodies'),
        ('Spectroscopy','Spectroscopy'),
    ]
    OBSERVATIONAL_TYPES = [

        ('Table Binary','Table Binary'),
        ('Table Character','Table Character'),
        ('Table Delimited','Table Delimited'),
    ]
    PROCESSING_LEVEL_TYPES = [
        ('Calibrated','Calibrated'),
        ('Derived','Derived'),
        ('Reduced','Reduced'),
        ('Raw','Raw'),
        #('Telemetry','Telemetry'),  Executive Decision made to leave this out.  6-27-2018.
    ]
    PURPOSE_TYPES = [
        ('Calibration','Calibration'),
        ('Checkout','Checkout'),
        ('Engineering','Engineering'),
        ('Navigation','Navigation'),
        ('Observation Geometry','Observation Geometry'),
        ('Science','Science'),

    ]
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    domain = models.CharField(max_length=MAX_CHAR_FIELD, choices=DOMAIN_TYPES, default='Atmosphere')
    discipline = models.CharField(max_length=MAX_CHAR_FIELD, choices=DISCIPLINE_TYPES, default='Atmospheres')
    processing_level = models.CharField(max_length=MAX_CHAR_FIELD, choices=PROCESSING_LEVEL_TYPES)
    purpose = models.CharField(max_length=MAX_TEXT_FIELD, choices=PURPOSE_TYPES)
    title = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD, choices=OBSERVATIONAL_TYPES, default='Not_Set')



    """
        name_label_case returns the title of the Product Observational in lowercase with underscores rather than spaces
    """
    def name_label_case(self):
        edit_name = self.title.lower()
        edit_name = replace_all(edit_name, ' ', '_')
        return edit_name

    """
       lid returns the lid associated with the Product_Observational label
    """
    def lid(self):
        edit_name = self.name_label_case()
        lid = 'urn:{0}:{1}:data_{2}:{3}'.format(self.bundle.user.userprofile.agency, self.bundle.name_lid_case(), self.processing_level.lower(), self.name_label_case())
        return lid
        

    """
       label returns the physical label location in ELSAs archive
    """
    def label(self):
        edit_name = '{}.xml'.format(self.name_label_case())
        return os.path.join(self.data.directory(), edit_name)



    # Label Constructors
    def build_base_case(self):
        
        # Locate base case Product_Collection template found in templates/pds4_labels/base_case/
        source_file = os.path.join(PDS4_LABEL_TEMPLATE_DIRECTORY, 'base_case')
        source_file = os.path.join(source_file, 'product_observational.xml')

        # Locate collection directory and create path for new label
        edit_name = '{}.xml'.format(self.name_label_case())
        label_file = os.path.join(self.data.directory(), edit_name)


        # Copy the base case template to the correct directory
        copyfile(source_file, label_file)
            
        return


    # Fillers
    """
        Fillers follow a set flow.
            1. Input the root element of an XML label.
                - We want the root because we can access all areas of the document through it's root.
            2. Find the areas you want to fill.
                - Always do find over a static search to ensure we are always on the right element.
                  (  ex. of static search ->    root[0] = Identification_Area in fill_base_case    )
                  Originally, ELSA used a static search for faster performance, but we found out
                  that comments in the XML label through the code off and we were pulling incorrect
                  elements.
            3. Fill those areas.
                - Fill is easy.  Just fill it.. with the information from the model it was called on,
                  self (like itself).
    """
    def fill_base_case(self, root):

        Identification_Area = root.find('{}Identification_Area'.format(NAMESPACE))


        logical_identifier = Identification_Area.find('{}logical_identifier'.format(NAMESPACE))
        logical_identifier.text = self.lid()
        title = Identification_Area.find('{}title'.format(NAMESPACE))
        title.text = self.title

        Observation_Area = root.find('{}Observation_Area'.format(NAMESPACE))
        Primary_Result_Summary = Observation_Area.find('{}Primary_Result_Summary'.format(NAMESPACE))
        processing_level = Primary_Result_Summary.find('{}processing_level'.format(NAMESPACE))
        processing_level = self.processing_level
        Science_Facets = Primary_Result_Summary.find('{}Science_Facets'.format(NAMESPACE))
        domain = Science_Facets.find('{}domain'.format(NAMESPACE))
        domain.text = self.domain
        discipline_name = Science_Facets.find('{}discipline_name'.format(NAMESPACE))
        discipline_name.text = self.discipline
        
        # ASK LYNN ABOUT THIS --------------------------------------------------------------------
        Investigation_Area = root.find('{}Investigation_Area'.format(NAMESPACE))
        # ----------------------------------------------------------------------------------------

        return root

    """
        Fillers follow a set flow.
            1. Input the root element of an XML label.
                - We want the root because we can access all areas of the document through it's root.
            2. Find the areas you want to fill.
                - Always do find over a static search to ensure we are always on the right element.
                  (  ex. of static search ->    root[0] = Identification_Area in fill_base_case    )
                  Originally, ELSA used a static search for faster performance, but we found out
                  that comments in the XML label through the code off and we were pulling incorrect
                  elements.
            3. Fill those areas.
                - Fill is easy.  Just fill it.. with the information from the model it was called on,
                  self (like itself).
    """
    def fill_observational(self, label_root, observational):
        Product_Observational = label_root

        File_Area_Observational = Product_Observational.find('{}File_Area_Observational'.format(NAMESPACE))

        Observational_Tag_Name = replace_all(self.type_of, ' ', '_')
        Observational_Tag = etree.SubElement(File_Area_Observational, Observational_Tag_Name)

        name = etree.SubElement(Observational_Tag, 'name')
        name.text = observational.name

        local_identifier = etree.SubElement(Observational_Tag, 'local_identifier')
          # NEED TO MAKE        local_identifier.text = observational.local_identifier() 

        offset = etree.SubElement(Observational_Tag, 'offset')
        offset.attrib['unit'] = 'byte'
        offset.text = observational.offset

        object_length = etree.SubElement(Observational_Tag, 'object_length')
        object_length.attrib['unit'] = 'byte'
        object_length.text = observational.object_length
   
        parsing_standard_id = etree.SubElement(Observational_Tag, 'parsing_standard_id')
        parsing_standard_id.text = 'PDS DSV 1'

        description = etree.SubElement(Observational_Tag, 'description')
        description.text = observational.description

        records = etree.SubElement(Observational_Tag, 'records')
        records.text = observational.records

        record_delimiter = etree.SubElement(Observational_Tag, 'record_delimiter')
        record_delimiter.text = 'Carriage-Return Line-Feed'
     
        field_delimiter = etree.SubElement(Observational_Tag, 'field_delimiter')
        field_delimiter.text = 'Need to Fix' # --------------------------------FIX ME----------

        # Start Record Delimited Section
        Record_Delimited = etree.SubElement(Observational_Tag, 'Record_Delimited')
        fields = etree.SubElement(Record_Delimited, 'fields')
        fields.text = observational.fields
        groups = etree.SubElement(Record_Delimited, 'groups')
        groups.text = observational.groups

        # Add loop  - Ask Lynn how he wants to do this, again.

        # End
        return Product_Observational
        
    """
    """
    # Meta
    def __str__(self):
        
        return "Product_Observational at: {}".format(self.title)





"""
12.1  Document

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
@python_2_unicode_compatible
class Product_Document(models.Model):

    # Attributes
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    acknowledgement_text = models.CharField(max_length=MAX_CHAR_FIELD)
    author_list = models.CharField(max_length=MAX_CHAR_FIELD)
    copyright = models.CharField(max_length=MAX_CHAR_FIELD)
    description = models.CharField(max_length=MAX_CHAR_FIELD)
    document_editions = models.CharField(max_length=MAX_CHAR_FIELD)
    document_name = models.CharField(max_length=MAX_CHAR_FIELD)
    doi = models.CharField(max_length=MAX_CHAR_FIELD)
    editor_list = models.CharField(max_length=MAX_CHAR_FIELD)
    publication_date = models.CharField(max_length=MAX_CHAR_FIELD)
    revision_id = models.CharField(max_length=MAX_CHAR_FIELD)

    # Meta
    def __str__(self):
        return self.document_name



    # Accessors
    """
    - absolute_url
      Returns the url to the Product Document Detail page.
    """
    def absolute_url(self):
        return reverse('build:product_document', args=[str(self.bundle.id),str(self.id)])

    def collection(self):
        return 'document'

    def directory(self):
        """
            Documents are found in the Document collection
        """
        collection_directory = os.path.join(self.bundle.directory(), 'document')
        return collection_directory


    def name_label_case(self):
        """
            This could be improved to ensure disallowed characters for a file name are not contained
            in name.
        """
        name_edit = self.document_name.lower()
        name_edit = replace_all(name_edit, ' ', '_')
        return name_edit


    def label(self):
        """
            label returns the physical label location in ELSAs archive
        """
        return os.path.join(self.directory(), self.name_label_case())

    def lid(self):
        return '{0}:document:{1}'.format(self.bundle.lid(), self.name_label_case())

    def reference_type(self):
        return 'document'





    # Builders
    def build_base_case(self):
        
        # Locate base case Product_Document template found in templates/pds4_labels/base_case/
        source_file = os.path.join(PDS4_LABEL_TEMPLATE_DIRECTORY, 'base_case')
        source_file = os.path.join(source_file, 'product_document.xml')

        # Locate collection directory and create path for new label
        label_file = os.path.join(self.directory(), self.name_label_case())


        # Copy the base case template to the correct directory
        copyfile(source_file, label_file)
            
        return

    """
        Fillers follow a set flow.
            1. Input the root element of an XML label.
                - We want the root because we can access all areas of the document through it's root.
            2. Find the areas you want to fill.
                - Always do find over a static search to ensure we are always on the right element.
                  (  ex. of static search ->    root[0] = Identification_Area in fill_base_case    )
                  Originally, ELSA used a static search for faster performance, but we found out
                  that comments in the XML label through the code off and we were pulling incorrect
                  elements.
            3. Fill those areas.
                - Fill is easy.  Just fill it.. with the information from the model it was called on,
                  self (like itself).
    """
    def fill_base_case(self, root):

        Product_Document = root

        # Fill in Identification_Area
        Identification_Area = Product_Document.find('{}Identification_Area'.format(NAMESPACE))

        logical_identifier = Identification_Area.find('{}logical_identifier'.format(NAMESPACE))
        logical_identifier.text =  'urn:{0}:{1}:{2}:{3}'.format(self.bundle.user.userprofile.agency, self.bundle.name_lid_case(), 'document', self.document_name) # where agency is something like nasa:pds

        version_id = Identification_Area.find('{}version_id'.format(NAMESPACE))
        version_id.text = '1.0'  # Can make this better

        title = Identification_Area.find('{}title'.format(NAMESPACE))
        title.text = self.document_name

        information_model_version = Identification_Area.find('information_model_version')
        #information_model_version.text = self.bundle.version.with_dots()   
        
        
        # Fill in Document
        Document = Product_Document.find('{}Document'.format(NAMESPACE))
        if self.revision_id:
            revision_id = etree.SubElement(Document, 'revision_id')
            revision_id.text = self.revision_id
        if self.document_name:
            document_name = etree.SubElement(Document, 'document_name')
            document_name.text = self.document_name
        if self.doi:
            doi = etree.SubElement(Document, 'doi')
            doi.text = self.doi
        if self.author_list:
            author_list = etree.SubElement(Document, 'author_list')
            author_list.text = self.author_list
        if self.editor_list:
            editor_list = etree.SubElement(Document, 'editor_list')
            editor_list.text = self.editor_list
        if self.acknowledgement_text:
            acknowledgement_text = etree.SubElement(Document, 'acknowledgement_text')
            acknowledgement_text.text = self.acknowledgement_text
        if self.copyright:
            copyright = etree.SubElement(Document, 'copyright')
            copyright.text = self.author_list
        if self.publication_date:  # this should always be true 
            publication_date = etree.SubElement(Document, 'publication_date')
            publication_date.text = self.publication_date
        if self.document_editions:
            document_editions = etree.SubElement(Document, 'document_editions')
            document_editions.text = self.document_editions   
        if self.description:
            description = etree.SubElement(Document, 'description')
            description.text = self.description     

        return root        


    def build_internal_reference(self, root, relation):
        """
            build_internal_reference needs to be completed
        """
        pass     


   





"""
10.1  Alias

Root Class:Product_Components
Role:Concrete

Class Description:The Alias class provides a single alternate name and identification for this product in this or some other archive or data system.

Steward:pds
Namespace Id:pds
Version Id:1.0.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product_Components	 	 	 
 	. Alias	 	 	 

Subclass	none	 	 	 

Attribute	alternate_id	0..1	 	 
        	alternate_title	0..1	 	 
        	comment	        0..1	 	 

Inherited Attribute	none	 	 	 
Association	        none	 	 	 
Inherited Association	none	 	 	 

Referenced from	Alias_List	 	 	 
"""
@python_2_unicode_compatible
class Alias(models.Model):

    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    alternate_id = models.CharField(max_length=MAX_CHAR_FIELD)
    alternate_title = models.CharField(max_length=MAX_CHAR_FIELD)
    comment = models.CharField(max_length=MAX_CHAR_FIELD)



    # Currently, the documentation says that none of these three fields: alternate_id, 
    # alternate_title, and comment are required within an Alias.  
    # However, it does not make a lot of sense to add a comment within an Alias tag without ever 
    # specifying an id or title.  Like what are you commenting about then, right?  So there should 
    # be some precedence set like ( alternate_id exclusive or alternate_title ) or comment.
    #
    # The truth table is as follows:
    #     ( alternate_id  EXCLUSIVE OR  alternate_title )   AND    comment
    #            1                                0                  0,1    *easy to see the comment
    #            0                                1                  0,1    *will not matter now
    def __str__(self):
        if self.alternate_id:
            return self.alternate_id
        elif self.alternate_title:
            return self.alternate_title
        else:
            return self.comment

    

    def build_alias(self, label_root):
        
         
        # Find Identification_Area
        Identification_Area = label_root.find('{}Identification_Area'.format(NAMESPACE))

        # Find Alias_List.  If no Alias_List is found, make one.
        Alias_List = Identification_Area.find('{}Alias_List'.format(NAMESPACE))
        if Alias_List is None:
            Alias_List = etree.SubElement(Identification_Area, 'Alias_List')

        # Add Alias information
        Alias = etree.SubElement(Alias_List, 'Alias')
        if self.alternate_id:
            alternate_id = etree.SubElement(Alias, 'alternate_id')
            alternate_id.text = self.alternate_id
        if self.alternate_title:
            alternate_title = etree.SubElement(Alias, 'alternate_title')
            alternate_title.text = self.alternate_title
        if self.comment:
            comment = etree.SubElement(Alias, 'comment')
            comment.text = self.comment
        
        
        return label_root


    class Meta:
        verbose_name_plural = 'Aliases'








"""
10.3  Citation_Information

Root Class:Product_Components
Role:Concrete

Class Description:The Citation_Information class provides specific fields often used in citing the product in journal articles, abstract services, and other reference contexts.

Steward:pds
Namespace Id:pds
Version Id:1.2.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product_Components	 	 	 
         	. Citation_Information	 	 	 

Subclass	none	 
	 	 
Attribute	author_list     	0..1	 	 
        	description      	1	 	 
        	editor_list      	0..1	 	 
        	keyword	                0..*	 	 
 	        publication_year	1	
 	 
Inherited Attribute	none	 	 	 
Association	        none	 	 	 
Inherited Association	none	 	 	 

Referenced from	Identification_Area	
""" 	 	 
@python_2_unicode_compatible
class Citation_Information(models.Model):

    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    author_list = models.CharField(max_length=MAX_CHAR_FIELD)
    description = models.CharField(max_length=MAX_CHAR_FIELD)
    editor_list = models.CharField(max_length=MAX_CHAR_FIELD)
    keyword = models.CharField(max_length=MAX_CHAR_FIELD)
    publication_year = models.CharField(max_length=MAX_CHAR_FIELD)
    
    # Builders
    def build_citation_information(self, label_root):
        
         
        # Find Identification_Area
        Identification_Area = label_root.find('{}Identification_Area'.format(NAMESPACE))

        # Find Alias_List.  If no Alias_List is found, make one.
        Citation_Information = Identification_Area.find('{}Citation_Information'.format(NAMESPACE))

        # Double check but I'm pretty sure Citation_Information is only added once.  
        #if Citation_Information is None:
        Citation_Information = etree.SubElement(Identification_Area, 'Citation_Information')

        # Add Citation_Information information
        if self.author_list:
            author_list = etree.SubElement(Citation_Information, 'author_list')
            author_list.text = self.author_list
        if self.editor_list:
            editor_list = etree.SubElement(Citation_Information, 'editor_list')        
            editor_list.text = self.editor_list
        if self.keyword:
            keyword = etree.SubElement(Citation_Information, 'keyword')  # Ask how keywords are saved #
            keyword.text = self.keyword
        publication_year = etree.SubElement(Citation_Information, 'publication_year')
        publication_year.text = self.publication_year
        description = etree.SubElement(Citation_Information, 'description')
        description.text = self.description
        return label_root

    # Meta
    def __str__(self):
        return 'Need to finish this.'









"""
    The Table model object can be one of the four accepted table types given in PDS4.
"""
@python_2_unicode_compatible
class Table(models.Model):

    OBSERVATIONAL_TYPES = [
        ('Table Base', 'Table Base'),
        ('Table Binary','Table Binary'),
        ('Table Character','Table Character'),
        ('Table Delimited','Table Delimited'),
    ]
    product_observational = models.ForeignKey(Product_Observational, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    observational_type = models.CharField(max_length=MAX_CHAR_FIELD, choices=OBSERVATIONAL_TYPES)
    local_identifier = models.CharField(max_length=MAX_CHAR_FIELD)
    offset = models.CharField(max_length=MAX_CHAR_FIELD)
    object_length = models.CharField(max_length=MAX_CHAR_FIELD)
    description = models.CharField(max_length=MAX_CHAR_FIELD)
    records = models.CharField(max_length=MAX_CHAR_FIELD)
    fields = models.CharField(max_length=MAX_CHAR_FIELD)
    groups = models.CharField(max_length=MAX_CHAR_FIELD)


    # meta
    def __str__(self):
        return 'Table Binary: {}'.format(self.name)




    






#    To Be Garbage Here✲






