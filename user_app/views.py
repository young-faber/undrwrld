from django.shortcuts import redirect, render
from django.contrib import auth
from user_app.forms import RegistrForm

def logout_view(request):
    auth.logout(request)
    return redirect("/")

def registr_view(request):
    if request.method == 'GET':
        registr_form = RegistrForm()
        context = {"registr_form": registr_form}
        return render(request,'user_app/registr.html', context)
    else: 
        registr_form = RegistrForm(data=request.POST)
        if registr_form.is_valid():
            registr_form.save() 
            return redirect('/')
        context = {"registr_form": registr_form}
        return render(request,'user_app/registr.html', context)


