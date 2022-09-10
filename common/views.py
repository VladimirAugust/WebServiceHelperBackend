from django.shortcuts import render

from trade.models import Good
from trade.views import GoodForm


def test_view(request):
    form = GoodForm(instance=Good.objects.get(pk=1))
    return render(request, 'test_form.html', {'form': form})



