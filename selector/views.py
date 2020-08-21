from django.shortcuts import render, redirect

# Create your views here.


def index(request):
    temp_dict = {
        'app_names': ['analyze', 'houseplants', 'stocks'],
    }
    return render(request, 'selector/index.html', temp_dict)


def redirect_to_app(request):
    """
    redirects application to appropriate django sub-app.
    """
    app_name = 'selector'
    if request.method == 'POST':
        print(request.POST)
        if 'selector_button' in request.POST:
            app_name = request.POST.get('selector_button')
    return redirect('%s:index' % app_name)
