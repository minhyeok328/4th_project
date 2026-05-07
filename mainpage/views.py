from django.shortcuts import render

# Create your views here.
def mainpage(request):
    return render(
		request,
		'mainpage.html',
		{
			"test_var": request.user.nickname if request.user.is_authenticated else "비로그인 상태"
		}
	)