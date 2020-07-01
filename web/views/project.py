from django.shortcuts import render


def project_list(request):
    print(request.tracer.user)
    print(request.tracer.price_policy)

    return render(request, 'project_list.html')
