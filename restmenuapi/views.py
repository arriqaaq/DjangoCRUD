from django.shortcuts import render
from restmenuapi.models import Restaurant, MenuItem
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import get_template
from django.http import JsonResponse
from restmenuapi.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

def index(request):
	visits = int(request.COOKIES.get('visits', '1'))
	reset_last_visit_time = False
	restaurants=Restaurant.objects.all()
	response = render(request,'restmenuapi/hello.html',{'restaurants':restaurants})
	if 'last_visit' in request.COOKIES:
		last_visit = request.COOKIES['last_visit']
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		if (datetime.now() - last_visit_time).seconds > 5:
			visits = visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True
		response = render(request,'restmenuapi/hello.html',{'restaurants':restaurants,'visits':visits})		
	
	if reset_last_visit_time:
		response.set_cookie('last_visit', datetime.now())
        response.set_cookie('visits', visits)			

	return response
	
def restaurantList(request,restaurant_id):
	restaurants=Restaurant.objects.filter(id=restaurant_id)
	return render(request,'restmenuapi/hello.html',{'restaurants':restaurants})


def newRestaurantItem(request):
	if request.method=='POST':
		print request.POST.get('name','')
		name=request.POST.get('name','')
		newRestaurant=Restaurant.objects.create(name=name)
		return HttpResponseRedirect(reverse('index'))
	else:
		return render(request,'restmenuapi/newrestaurant.html')


def editRestaurantItem(request,restaurant_id):
	editedRestaurant=Restaurant.objects.get(id=restaurant_id)
	if request.method =='POST':
		name=request.POST.get('name','')
		if name:
			editedRestaurant.name=request.POST.get('name','')
			editedRestaurant.save()
		return HttpResponseRedirect(reverse('index'))
	else:
		return render(request,'restmenuapi/editrestaurant.html',{'restaurant_id':restaurant_id,'i':editedRestaurant})

def deleteRestaurantItem(request,restaurant_id):
	deletedRestaurant=Restaurant.objects.get(id=restaurant_id)
	deleteditems=MenuItem.objects.filter(id=deletedRestaurant.id)
	print "yayyyyy", deleteditems
	if request.method=='POST':
		for i in deleteditems:
			print "Oh hO: ",i.id
			i.delete()
		deletedRestaurant.delete()
		return HttpResponseRedirect(reverse('index'))
	else:
		return render(request,'restmenuapi/deleterestaurant.html',{'restaurant_id':restaurant_id,'i':deletedRestaurant})

def restaurantMenu(request,restaurant_id):
	restaurant=Restaurant.objects.get(id=restaurant_id)
	items=MenuItem.objects.filter(restaurant=restaurant)
	return render(request,'restmenuapi/menu.html',{'restaurant':restaurant,'items':items})

def newMenuItem(request,restaurant_id):
	restaurant=Restaurant.objects.get(id=restaurant_id)
	if request.method=='POST':
		name=request.POST.get('name','')
		MenuItem.objects.create(name=name,restaurant=restaurant)
		return HttpResponseRedirect(reverse('menu',args=(restaurant_id,)))
	else:
		return render(request,'restmenuapi/newMenuItem.html',{'restaurant_id':restaurant_id})

def editMenuItem(request,menu_id):
	editedItem=MenuItem.objects.get(id=menu_id)
	if request.method =='POST':
		name=request.POST.get('name','')
		if name:
			editedItem.name=request.POST.get('name','')
			editedItem.save()
			return HttpResponseRedirect(reverse('menu',args=(editedItem.restaurant.id,)))
	else:
#		return render_template('editMenuItem.html',restaurant_id=restaurant_id,menu_id=menu_id,i=editedItem)
		return render(request,'restmenuapi/editMenuItem.html',{'i':editedItem})

def restaurantJson(request):
	restaurantall=Restaurant.objects.all()
	RestaurantItems=[i.serialize for i in restaurantall]
	return JsonResponse({'Restaurants':RestaurantItems})

def register(request):



    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

   	if request.session.test_cookie_worked():
		print "DOne!!!!!!!!!!!!111"
		request.session.delete_test_cookie()


    # Render the template depending on the context.
    return render(request,
            'restmenuapi/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/restmenuapi/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'restmenuapi/login.html', {})

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/restmenuapi/')