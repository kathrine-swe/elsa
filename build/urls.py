# Stdlib imports

# Core Django imports
from django.conf.urls import url, include

# Third-party app imports

# Imports from apps
from . import views



app_name='build'
urlpatterns = [
    # Alias
    url(r'^(?P<pk_bundle>\d+)/alias/$', views.alias, name='alias'),

    # Build
    url(r'^$', views.build, name='build'),

    # Bundle
    url(r'^(?P<pk_bundle>\d+)/$', views.bundle, name='bundle'), # Secure
    url(r'^(?P<pk_bundle>\d+)/confirm_delete/$', views.bundle_delete, name='bundle_delete'), # Secure
    url(r'^(?P<pk_bundle>\d+)/download/$', views.bundle_download, name='bundle_download'), # Need to secure.

    # Citation_Information
    url(r'^(?P<pk_bundle>\d+)/citation_information/$', views.citation_information, name='citation_information'),

    # Collections


    # Context


    # Data
    url(r'^(?P<pk_bundle>\d+)/data/$', views.data, name='data'),
    url(r'^(?P<pk_bundle>\d+)/data/(?P<pk_product_observational>\d+)/$', views.product_observational, name='product_observational'),

    # Document
    url(r'^(?P<pk_bundle>\d+)/document/$', views.document, name='document'),
    url(r'^(?P<pk_bundle>\d+)/document/product_document/(?P<pk_product_document>\d+)/$', views.product_document, name='product_document'),


    # XML_Schema --> A view that no one sees.  So no xml_schema url.  This might even be removed 
    # completely from PDS4





    # TEST
]
