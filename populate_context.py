import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elsa.settings')

import django
django.setup()

from context.models import *
from lxml import etree
import urllib2


# The following is a variable containing a string representation of the URL where JPL's Starbase
# repository holds the context products
STARBASE_CONTEXT = 'https://starbase.jpl.nasa.gov/pds4/context-pds4/'


"""
get_context_products_for

input: a string containing the type of context product the user is looking for
       examples: 'instrument', 'investigation', 'target'

output: a list of all products for that context type
"""
def get_context_products_for(context_type):
    STARBASE_PRODUCTS = STARBASE_CONTEXT + context_type
    print STARBASE_PRODUCTS

    html_arr = urllib2.urlopen(STARBASE_PRODUCTS).readlines()
    product_list = []
    for string in html_arr:
        if '.xml' in string:
            #print string
            root = etree.fromstring(string)
            #print root
            product = root[1][0]
#            print product.text

            #product = product.text.split('.')
            product_list.append(product.text)
    return product_list


"""
This is the script to autopopulate context products.
The context types covered in this script are:
    - investigation
"""
def populate():

    # created is a list of elements that were created by this population script
    created = []


    # grab the whole list of investigations from Starbase
    investigations = get_context_products_for('investigation')

    # for each investigation, we want to add this to ELSA's database
    for investigation in investigations:

        # we need the url where the label exists
        investigation_url = STARBASE_CONTEXT + 'investigation/' + investigation

        # we also need specific information, ie investigation details
        # investigation_detail is a list containing [type_of, name, version, file extension]
        investigation_detail = investigation.split('.')
       
        # we want to create the object in our database if it does not already exist
        i = Investigation.objects.get_or_create(
            name=investigation_detail[1], 
            type_of=investigation_detail[0], 
            version=int(investigation_detail[2]), 
            starbase_label=investigation_url
        )

        # if the object was created, we want to append it to our created list so we can
        # print what was created for our own sanity
        if i[1] == True:
            i[0].save()
            created.append(i[0])

    for elt in created:
        print "New object: {0}".format(elt)


        




if __name__ == '__main__':
    print("\nSTARTING ELSA POPULATION SCRIPT -- CONTEXT MODELS.")
    print("@PieceOfKayk. July 2018")
    populate()
    print("Population successful.\n")

    #version_set = Version.objects.all()
    #print 'The current version models in ELSA are:'
    #for v in version_set:
    #    print v

    
