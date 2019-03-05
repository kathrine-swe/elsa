import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elsa.settings')

import django
import time
django.setup()

from build.models import Version

def populate():


    # First, create a list of dictionaries containing the versions and their attributes.
    versions = [
        {
            'num':'1A10',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1A10.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1A10.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
        {
            'num':'1A00',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1A00.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1A00.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
        {
            'num':'1900',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1900.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1900.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
        {
            'num':'1800',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1800.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1800.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
        {
            'num':'1700',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1700.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1800.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
        {
            'num':'1410',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1410.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1800.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
        {
            'num':'1300',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1300.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1800.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
        {
            'num':'1000',
            'xml_model':'http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1000.sch',
            'xmlns':'http://pds.nasa.gov/pds4/pds/v1',
            'xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation':'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1800.xsd',
            'schematypens':'http://purl.oclc.org/dsdl/schematron',

        },
    ]

    print '------------------------------ ADDING VERSIONS -----------------------------------------\n'
    for version in versions:
        '------------------------------- Version Information ------------------------------------\n'
        print 'Version: {}'.format(version['num'])
        print 'xml_model: {}'.format(version['xml_model'])
        print 'xmlns: {}'.format(version['xmlns'])
        print 'xsi: {}'.format(version['xsi'])
        print 'schemaLocation: {}'.format(version['schemaLocation'])
        print 'schematypens: {}'.format(version['schematypens'])
        print '\n\n...Adding Version {}...'.format(version['num'])
        add_version(version['num'], version['xml_model'], version['xmlns'], version['xsi'], version['schemaLocation'], version['schematypens'])
        print '\n\n...Version {} Added...'.format(version['num'])

def add_version(num, xml_model, xmlns, xsi, schemaLocation, schematypens):
    v = Version.objects.get_or_create(num=num, xml_model=xml_model, xmlns=xmlns, xsi=xsi, schemaLocation=schemaLocation, schematypens=schematypens)
    v[0].save()



if __name__ == '__main__':
    print("\nSTARTING ELSA POPULATION SCRIPT -- VERSION MODELS.")
    print("@PieceOfKayk. July 2018")
    s1 = time.time()
    populate()
    s2 = time.time()
    print("Population successful.\nTime elapsed: ", (s2 - s1) )

    version_set = Version.objects.all()
    print 'The current version models in ELSA are:'
    for v in version_set:
        print v

    
