

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elsa.settings')

import django
django.setup()

from context.models import *
from lxml import etree
import time
import urllib2

# Declare Global Variables
created = []

# The following is a variable containing a string representation of the URL where JPL's Starbase
# repository holds the context products
STARBASE_CONTEXT = 'https://starbase.jpl.nasa.gov/pds4/context-pds4/'

# The following is a variable containing a list of current version ids (vids) found for products in 
# Starbase
#     This requires upkeep by a developer
#     Below is a list of current vids
#     If this list is not up to date, this function will miss things.
CURRENT_VIDS = ['1.0', '1.1'] # max vid so far is 1.13 




"""
Takes two lists and makes them one list of 2-tuples.
Example: list1 = [ 0, 1, 2], list2 = [ 'a', 'b', 'c'], list3 = ['elsa', 'pds', 'atmos']
		The returned list is then [ (0, 'a', 'elsa'), (1, 'b', 'pds'), (2, 'c', 'atmos') ]
"""
def list_of_tuples(list1, list2):
    return list(map(lambda x, y: (x,y), list1, list2))


"""
get_product_list(string)

input: a string containing the type of context product the user is looking for
       examples: 'instrument', 'investigation', 'target'

output: a list of all products for that context type
"""
def get_product_list(context_type):
    STARBASE_PRODUCTS = STARBASE_CONTEXT + context_type
    #print STARBASE_PRODUCTS

    html_arr = urllib2.urlopen(STARBASE_PRODUCTS).readlines()
    product_list = []
    for string in html_arr:
        if '.xml' in string:
            #print string
            root = etree.fromstring(string)
            #print root
            product = root[1][0]
            product_list.append(product.text)
    return product_list

"""
get_product_dict(url)

input: a string representation of the url where the product label is located

output: a dictionary containing the product's lid, vid, and internal references.

"""
def get_product_dict(url):

    product_dict = {}
    lid_references = []
    reference_types = []

    # Turn label into a tree and get root of tree
    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(urllib2.urlopen(url), parser=parser)
    label_root = tree.getroot()


    # Get proper product information for dictionary
    #     Note: For each internal reference there should be exactly one lid_reference or
    #            lidvid_reference and exactly one reference_type.
    #     Note: When a lidvid_reference is given, it will be modified to be the equivalent
    #            lid_reference.


    # Get lid for product
    product_dict['lid'] = label_root[0][0].text
            #print elt, " = ", element.text

    # Get vid for product
    product_dict['vid'] = float(label_root[0][1].text)

 
    for element in label_root.iter():
        #print element
        elt = element.tag.split('}')[1] # Eliminates namespace from tag

        # Get lid_references for internal references
        if elt == 'lid_reference':

            # Append lid_reference to the list of lid_references
            lid_references.append(element.text)
            #print elt, " = ", element.text

        # Get lidvid_references for internal references
        elif elt == 'lidvid_reference':

            # Modify lidvid to be a lid reference
            e = element.text.split('::')[0]

            # Append lid_reference equivalent of lidvid_reference to the list of lid_references
            lid_references.append(e)
      
            #print elt, " = ", element.text                

        # Get reference_types for internal references
        elif elt == 'reference_type':

            # Append reference_type to the list of reference_types
            reference_types.append(element.text)
            #print elt, " = ", element.text

    # Save the internal references into the product's dictionary
    product_dict['internal_references'] = list_of_tuples(lid_references, reference_types)

    return product_dict


# get_internal_refs
# This function finds a specific type of internal reference from a given type of product.
# It will return a list, empty or nonempty.
#
# input:
#     product_dict : the product_dict already grabs all of the internal_references for 
#                    a product which are stored under the key 'internal_references'
#                    (See get_product_dict() for more information). 
#     source_product : the product we want to find the internal references for
#     target_product : the type of product we want the internal reference to be
# 
# output:
#     a list of objects of type target_product that are related to source_product
def get_internal_references(product_dict, source_product, target_product):

    # Declare list of internal references to be returned to the user containing
    # all of the internal references that match the given source product to target product
    # relation.
    matched_refs = []
    matched_objs = []

    # Determine the source_product to target_product relation
    relation = "{0}_to_{1}".format(source_product, target_product)

    # Get the list of internal references where for each internal reference,
    # the internal reference is a 2-tuple of (lid_reference, reference_type)
    internal_references = product_dict['internal_references']
    for internal_ref in internal_references:
        if internal_ref[1] == relation:
            # Search objects to get the object related to the internal_reference
            # of type target_product given its lid
            ir_obj = get_lid_to_object_queryset(target_product, internal_ref[0])
            matched_refs.append(ir_obj)

    # Return all the internal references that matched the given source product to target 
    # product relations
    return matched_refs


# Finds the associated object of type product_type given the product's lid
def get_lid_to_object_queryset(product_type, lid):
    print product_type
    print lid
    if product_type == 'investigation':
        product = Investigation.objects.get_or_create(lid=lid)
        # If we end up creating an object at this point, we have an error in Starbase.
        # ELSA takes a top down approach while crawling. If we are finding a queryset
        # for investigation objects, then we are asking to do so in something like
        # instrument host, instrument, or target so that we can reference the product
        # back to an investigation. If we find an investigation that needs to be created at
        # this point, seeing as ELSA's crawler crawls investigation first, we have an error
        # where a product like an instrument host, instrument, target, etc., has a reference
        # to an investigation that does not exist in Starbase. This is against PDS4.
        if product[1]:
            return "STARBASE ERR: Starbase is missing an Investigation object"
        else:
            return product[0]
    elif product_type == 'instrument_host':
        return Instrument_Host.objects.get(lid=lid)
    


#
#
#
def investigation_crawl():

    # STARBASE FIXES
    i = Investigation.objects.get_or_create(name='support_archives', type_of='mission', lid='urn:nasa:pds:context:investigation:mission.support_archives', vid=1.0)
    if i[1] == True:
        created.append(i[0])
 
    # INVESTIGATION CRAWL
    # grab the whole list of investigations from Starbase
    investigations = get_product_list('investigation')

    # for each investigation, we want to create an Investigation object in ELSA's database
    for inv in investigations:
        print "\n\nInvestigation: ", inv

        # we need the url where the label exists
        investigation_url = STARBASE_CONTEXT + 'investigation/' + inv
        print "URL: ", investigation_url

        # we want our crawler to grab specified information from the labels
        # these details about the investigation will be used to fill the
        # ELSA database
        #
        #   definition:
        #     investigation_detail = [type_of, name, version, file extension]
        #
        investigation_detail = inv.split('.')
        investigation_detail[2] = float(investigation_detail[1][-1:] + '.' + investigation_detail[2])
        investigation_detail[1] = investigation_detail[1][:-2]
        print "Investigation Detail: ", investigation_detail

        # we want the latest       
        # we want to create the object in our database if it does not already exist

        #
        #  get_or_create returns a 2-tuple containing the object and a boolean indicating whether
        #  or not the object was created.
        #    i = ( object, created )
        print "name: ", investigation_detail[1]
        print "type_of: ", investigation_detail[0]
        i = Investigation.objects.get_or_create(
                name=investigation_detail[1], 
                type_of=investigation_detail[0], 
            )
        print i
        
        # Get product dictionary
        product_dict = get_product_dict(investigation_url)

        # if the object was created, then it is the first product of its name
        # and investigation type so we want to do a few things:
        #     1. Save and append object to our created list so we can
        #        print what was created later for our own sanity
        if i[1] == True:
            i[0].vid = product_dict['vid']
            i[0].lid = product_dict['lid']
            i[0].starbase_label = investigation_url
            i[0].save()
            created.append(i[0])
            print "NEW OBJECT: ", i[0].vid, i[0].lid


        # If the object already exists in our database, we want to make sure the database object
        # is the latest version of the product, designated by the vid (or version_id)
        else:
            # Compare if the vid in our investigation detail is greater than the vid associated
            # with our investigation object, i[0].
            if( i[0].vid < product_dict['vid'] ):
                print "HIGHER VID FOUND: ", i[0].vid, " < ", product_dict['vid']
                print type(i[0].vid), type(product_dict['vid'])

                # Modify object i to be the last version of i
                i[0].vid = product_dict['vid']
                i[0].lid = product_dict['lid']
                i[0].starbase_label = investigation_url
                i[0].save()
                created.append(i[0])

                print "MODIFIED OBJ: ", i[0].vid, i[0].lid





def instrument_host_crawl():

    # STARBASE FIXES
    j = Instrument_Host.objects.get_or_create(name='unk', type_of='unk', lid='urn:nasa:pds:context:instrumenthost:unk.unk', vid=1.0)
    if j[1] == True:
        created.append(j[0])




    # INSTRUMENT_HOST CRAWL


    # grab the whole list of instrument hosts from Starbase
    instrument_hosts = get_product_list('instrument_host')

    # for each investigation, we want to create an Instrument_Host object in ELSA's database
    for instrument_host in instrument_hosts:
        print "\n\nInstrument host: ", instrument_host

        # we need the url where the label exists
        instrument_host_url = STARBASE_CONTEXT + 'instrument_host/' + instrument_host
        print "URL: ", instrument_host_url

        # we want our crawler to grab specified information from the labels
        # these details about the investigation will be used to fill the
        # ELSA database
        #
        #   definition:
        #     instrument_host_detail = [type_of, name, version, file extension]
        #
        instrument_host_detail = instrument_host.split('.')
        instrument_host_detail[2] = float(instrument_host_detail[1][-1:] + '.' + instrument_host_detail[2])
        instrument_host_detail[1] = instrument_host_detail[1][:-2]
        print "Instrument_Host Detail: ", instrument_host_detail

        # we want the latest       
        # we want to create the object in our database if it does not already exist

        # Get product dictionary
        product_dict = get_product_dict(instrument_host_url)

        # Get investigation object(s)
        #investigation_set = get_internal_references(product_dict, 'instrument_host', 'investigation')

        #
        #  get_or_create returns a 2-tuple containing the object and a boolean indicating whether
        #  or not the object was created.
        #    i = ( object, created )
        i = Instrument_Host.objects.get_or_create(
                #investigation=investigation_set[0],
                name=instrument_host_detail[1], 
                type_of=instrument_host_detail[0], 
            )
        print i
        
        # Get product dictionary by crawling the instrument host label on Starbase
        product_dict = get_product_dict(instrument_host_url)

        # If the object was retrieved, ie. already exists in our database, we want to make sure 
        # the database object is the latest version of the product, designated by the vid (or 
        # version_id)
        if i[1] == False :
            # Compare if the vid in our investigation detail is greater than the vid associated
            # with our investigation object, i.
            if( i[0].vid < product_dict['vid'] ):
                print "HIGHER VID FOUND: ", i[0].vid, " < ", product_dict['vid']
                print type(i[0].vid), type(product_dict['vid'])

                # Modify object i to be the last version of i
                i[0].vid = product_dict['vid']
                i[0].lid = product_dict['lid']
                i[0].starbase_label = instrument_host_url
                i[0].save()
                created.append(i[0])

                print "MODIFIED OBJ: ", i[0].vid, i[0].lid


        # if the object was created, then it is the first product of its name
        # and investigation type so we want to do a few things:
        #     1. Get the investigation that the instrument host is related to
        #        
        #     2. Save and append object to our created list so we can
        #        print what was created later for our own sanity
 
        else:
            # Get investigation object(s)
            investigation_set = get_internal_references(product_dict, 'instrument_host', 'investigation')
            # Add investigation object(s) relation to instrument host object
            if len(investigation_set) == 0:
                print "No investigations found"
            else:
                for inv in investigation_set:
                    i[0].investigation.add(inv)
            i[0].vid = product_dict['vid']
            i[0].lid = product_dict['lid']
            i[0].starbase_label = instrument_host_url
            i[0].save()
            created.append(i[0])
            print "New elt i: ", i[0].vid, i[0].lid

def instrument_crawl():
    # INSTRUMENT CRAWL
    # grab the whole list of instruments from Starbase
    instruments = get_product_list('instrument')

    # for each investigation, we want to create an Instrument_Host object in ELSA's database
    for instrument in instruments:
        print "\n\nInstrument: ", instrument

        # we need the url where the label exists
        instrument_url = STARBASE_CONTEXT + 'instrument/' + instrument
        print "URL: ", instrument_url

        # we want our crawler to grab specified information from the labels
        # these details about the investigation will be used to fill the
        # ELSA database
        #
        #   definition:
        #     instrument_detail = [type_of, name, (sometimes another name), version, file extension]
        #
        instrument_detail = instrument.split('.')
        print "DEBUG:  ", instrument_detail
        instrument_detail[2] = float(instrument_detail[-3][-1:] + '.' + instrument_detail[-2])
        instrument_detail[1] = instrument_detail[1][:-2]
        print "Instrument Detail: ", instrument_detail

        # we want the latest       
        # we want to create the object in our database if it does not already exist

        # Get product dictionary
        product_dict = get_product_dict(instrument_url)

        # Get associated investigation object(s)
        #investigation_set = get_internal_references(product_dict, 'instrument', 'investigation')

        # Get associated instrument host object(s)
        #instrument_host_set = get_internal_references(product_dict, 'instrument', 'instrument_host')

        #
        #  get_or_create returns a 2-tuple containing the object and a boolean indicating whether
        #  or not the object was created.
        #    i = ( object, created )
        i = Instrument.objects.get_or_create(
                #investigation=investigation_set[0],
                name=instrument_detail[1], 
                type_of=instrument_detail[0], 
            )
        print i
        
        # Get product dictionary by crawling the instrument host label on Starbase
        product_dict = get_product_dict(instrument_url)

        # If the object was retrieved, ie. already exists in our database, we want to make sure 
        # the database object is the latest version of the product, designated by the vid (or 
        # version_id)
        if i[1] == False :
            # Compare if the vid in our investigation detail is greater than the vid associated
            # with our investigation object, i.
            if( i[0].vid < product_dict['vid'] ):
                print "HIGHER VID FOUND: ", i[0].vid, " < ", product_dict['vid']
                print type(i[0].vid), type(product_dict['vid'])

                # Modify object i to be the last version of i
                i[0].vid = product_dict['vid']
                i[0].lid = product_dict['lid']
                i[0].starbase_label = instrument_url
                i[0].save()
                created.append(i[0])

                print "MODIFIED OBJ: ", i[0].vid, i[0].lid


        # if the object was created, then it is the first product of its name
        # and investigation type so we want to do a few things:
        #     1. Get the investigation that the instrument host is related to
        #        
        #     2. Save and append object to our created list so we can
        #        print what was created later for our own sanity
 
        else:
            # Get investigation object(s)
            #investigation_set = get_internal_references(product_dict, 'instrument', 'investigation')
            # Get instrument host object(s)
            instrument_host_set = get_internal_references(product_dict, 'instrument', 'instrument_host')
            # Add investigation object(s) relation to instrument host object
            #if len(investigation_set) == 0:
            #    print "No investigations found"
            #for inv in investigation_set:
            #    i[0].investigation.add(inv)

            # Add investigation object(s) relation to instrument host object
            if len(instrument_host_set) == 0:
                print "No investigations found"
            else:
                for ins_host in instrument_host_set:
                    i[0].instrument_host.add(ins_host)
            i[0].vid = product_dict['vid']
            i[0].lid = product_dict['lid']
            i[0].starbase_label = instrument_url
            i[0].save()
            created.append(i[0])
            print "New elt i: ", i[0].vid, i[0].lid

                








































"""
This is the script to autopopulate context products.
The context types covered in this script are:
    - investigation
"""
def populate():

    # created is a list of elements that were created by this population script
    # currently created is empty bc nothing has been added to it.
    investigation_crawl()
    instrument_host_crawl()
    instrument_crawl()

    for elt in created:
        print "New object: {0}".format(elt.name)


if __name__ == '__main__':
    print("\nSTARTING ELSA POPULATION SCRIPT -- CONTEXT MODELS.")
    print("January 2019 (k)")
    s1 = time.time()
    populate()
    s2 = time.time()
    print "POPULATION SUCCESSFUL"
    print("Time Elapsed: ", (s2 - s1), "\nNumber of objects added: ", len(created))
