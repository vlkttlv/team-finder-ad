from django.core.paginator import Paginator

from team_finder.constants import PROJECTS_PER_PAGE


def paginate_queryset(queryset, request, per_page=PROJECTS_PER_PAGE):
    """Возвращает page_obj для переданного queryset."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
