# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render






# Create your views here.

@login_required
def build(request): 
    print 'DEBUG START --------------------'
    form_bundle = BundleForm(request.POST or None)
    form_collections = CollectionsForm(request.POST or None)
    context_dict = {
        'form_bundle':form_bundle,
        'form_collections':form_collections,
        'user':request.user,
    }

    if form_bundle.is_valid() and form_collections.is_valid():
        print 'all forms valid'

        # Check Uniqueness
        bundle_name = form_bundle.cleaned_data['name']
        bundle_user = request.user
        bundle_count = Bundle.objects.filter(name=bundle_name, user=bundle_user).count()
        # If user and bundle name are unique, then...
        if bundle_count == 0:

            # Create Bundle model.
            bundle = form_bundle.save(commit=False)
            bundle.user = request.user
            bundle.status = 'b' # b for build.  New Bundles are always in build stage first.
            bundle.save()

            # Build PDS4 Ccmpliant Bundle directory in User Directory.
            bundle.build_directory

            # Create Product_Bundle model.
            product_bundle = ProductBundleForm().save(commit=False)
            product.bundle = bundle
            product.save()

            # Build Product_Bundle label
            bundle.build_product_bundle

            # Create Collections Model Object and list of Collections, list of Collectables
            collections = form.save(commit=False)
            collections.bundle = bundle
            collections.save()
            
            # Create PDS4 compliant directories for each collection within the bundle.            
            collections.build_directories


            # Build Product_Collection label for each collection within the bundle.
            collections.build_product_collection
           
            # Further develop context_dict entries for templates            
            context_dict['Bundle'] = bundle
            context_dict['Product_Bundle'] = Product_Bundle.objects.get(bundle=bundle)
            context_dict['Product_Collection_Set'] = Product_Collection.objects.filter(bundle=bundle)

            return render(request, 'build/two.html', context_dict)



#  UPDATE ON THE FOLLOWING COMMENT (May 2019)
        # This can be fixed using our validator solution



# ---- CHECK THIS OUT ----
        # If user has a bundle with that name, then...
        # !! --- FIX ME --- !! --- FIX ME --- !! --- FIX ME --- !! --- FIX ME --- !! --- FIX ME --- !!
        # This should just simply present as an error on screen.  It does when you add a document.
        #else:    
         #   return HttpResponse("You already have a bundle with that name. Please press back on your browser and provide a new name.")
# ---- END CHECK ----            



    return render(request, 'build/build.html', context_dict)

# The bundle_detail view is the page that details a specific bundle.
@login_required
def bundle(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    bundle_user = bundle.user


    print 'BEGIN bundle_detail VIEW'
    if request.user == bundle.user:
        context_dict = {
            'bundle':bundle
        }
        return render(request, 'build/bundle/bundle.html', context_dict)

    else:
        return redirect('main:restricted_access')

# The bundle_download view is not a page.  When a user chooses to download a bundle, this 'view' manifests and begins the downloading process.

def bundle_download(request, pk_bundle):
    # Grab bundle directory
    bundle = Bundle.objects.get(pk=pk_bundle)

    print 'BEGIN bundle_download VIEW'
    print 'Username: {}'.format(request.user.username)
    print 'Bundle directory name: {}'.format(bundle.get_name_directory())
    print 'Current working directory: {}'.format(os.getcwd())
    print settings.TEMPORARY_DIR
    print settings.ARCHIVE_DIR

    # Make tarfile
    #    Note: This does not run in build directory, it runs in elsa directory.  
    #          Uncomment print os.getcwd() if you need the directory to see for yourself.
    tar_bundle_dir = '{}.tar.gz'.format(bundle.get_name_directory())
    temp_dir = os.path.join(settings.TEMPORARY_DIR, tar_bundle_dir)
    source_dir = os.path.join(settings.ARCHIVE_DIR, request.user.username)
    source_dir = os.path.join(source_dir, bundle.get_name_directory())
    make_tarfile(temp_dir, source_dir)

    # Testing.  See if simply bundle directory will download.
    # Once finished, make directory a tarfile and then download.
    file_path = os.path.join(settings.TEMPORARY_DIR, tar_bundle_dir)


    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-tar")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    return HttpResponse("Download did not work.")

# The bundle_delete view is the page a user sees once they select the delete bundle button.  This view gives the user an option to confirm or take back their choice.  This view could be improved upon.
@login_required
def bundle_delete(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    user = bundle.user
    delete_bundle_form = ConfirmForm(request.POST or None)

    context_dict = {}
    context_dict['bundle'] = bundle
    context_dict['user'] = user
    context_dict['delete_bundle_form'] = delete_bundle_form
    context_dict['decision'] = 'has yet to have the chance to be'

    # Secure:  If current user is the user associated with the bundle, then...
    if request.user == user:
        if delete_bundle_form.is_valid():
            print 'form is valid'
            print 'decision: {}'.format(delete_bundle_form.cleaned_data["decision"])
            decision = delete_bundle_form.cleaned_data['decision']
            if decision == 'Yes':
                context_dict['decision'] = 'was'
                success_status = remove.bundle_dir_and_model(bundle, user)
                if success_status:
                    return redirect('../../success_delete/')


            if decision == 'No':
                # Go back to bundle page
                context_dict['decision'] = 'was not'

        return render(request, 'build/bundle/confirm_delete.html', context_dict)

    # Secure: Current user is not the user associated with the bundle, so...
    else:
        return redirect('main:restricted_access')
