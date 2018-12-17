# crawl.py
# authors:
#    k
# purpose:
#    Elsa uses crawl.py within the  Crawl Starbase app to scour JPL's Starbase Repository for PDS4 
#    Label information.

from lxml import etree
import urllib


# FINAL VARIABLES

"""
The PRODUCT_TYPE_LIST is the list of products we can devour from Starbase
They can be found at https://starbase.jpl.nasa.gov/pds4/context-pds4/
"""
PRODUCT_TYPE_LIST = [
    'agency',
    'airborne',
    'attribute',
    'class',
    'facility',
    'instrument',
    'instrument_host',
    'investigation',
    'node',
    'personnel-affiliate',
    'resource',
    'service',
    'target',
    'telescope',
]

"""
get_product_list gets a list of products of a specified type from Starbase.  This list will...
"""
def get_product_list(product_type):


    print '---------------- Crawl Product List --------------------'
    print '--------------------- DEBUGGER -------------------------'
    print "\n\n"
    print 'Product Type: {}'.format(product_type)
    print "\n\n"

    # Head to Starbase
    starbase_url = 'https://starbase.jpl.nasa.gov/pds4/context-pds4/{}/Product/'.format(product_type)
    html = urllib.urlopen(starbase_url).readlines()

    # Grab product list
    product_list = []
    for line in html:
        if 'PDS4_' in line:
            # then the line contains link information to a product so we want to grab the html tag 
            # containing the product url.  The value is the extension to be placed after /Product/ in 
            # starbase_url as seen below.
            root = etree.fromstring(line)
            url_tag_for_product = root[0][0]
            product_url_ending = url_tag_for_product.attrib.get('href')            
            starbase_url_product = "https://starbase.jpl.nasa.gov/pds4/context-pds4/{0}/Product/{1}".format(product_type, product_url_ending)

            # Now we go to the starbase url for the individual product and grab the information that we would like.
            starbase_text_product = urllib.urlopen(starbase_url_product).readlines()
            for row in starbase_text_product:
                print row

            # 

    #return product_list

def get_product_list_information(product_type, product_list):
    print '--------------------- Crawl Product List for Titles --------------------'
    print '------------------------------ DEBUGGER --------------------------------'
    print '\n\n'
    for product in product_list:
        starbase_url = 'https://starbase.jpl.nasa.gov/pds4/context-pds4/'

get_product_list('instrument')
    
