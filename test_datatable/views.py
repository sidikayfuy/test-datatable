from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import TemplateView

from .models import Studies


class DatatableView(TemplateView):
    template_name = 'test_datatable/datatable.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['fields'] = [[i.name, type(i).__name__, i.verbose_name] for i in Studies._meta.fields[::] if i.name != 'id']
        return data


def ajaxTable(request):
    start = int(request.GET['start'])
    per_page = int(request.GET['length'])
    order_column = int(request.GET['order[0][column]'])
    order_direction = request.GET['order[0][dir]']

    fields = ['patient_fio', 'patient_birthdate', 'study_uid', 'study_date', 'study_modality__name']

    if order_column < len(fields):
        order_field = fields[order_column]
    else:
        order_field = 'patient_fio'

    if order_direction == 'desc':
        order_field = '-' + order_field

    studies = Studies.objects.all()

    for field in fields:
        if 'date' in field:
            search_date = request.GET.get(field)
            if search_date:
                studies = studies.filter(
                    Q(**{field: search_date})
                )
            filter_date = request.GET.get(field + 'filter')
            if filter_date:
                filter_date2 = request.GET.get(field + 'filter2')
                filter_type = request.GET.get(field + 'filtertype')
                if filter_date2:
                    if filter_type == '3':
                        studies = studies.filter(
                            Q(**{field+'__gte': filter_date, field+'__lte': filter_date2})
                        )
                    if filter_type == '4':
                        studies = studies.exclude(
                            Q(**{field+'__gte': filter_date, field+'__lte': filter_date2})
                        )
                else:
                    if filter_type == '0':
                        studies = studies.exclude(
                            Q(**{field: filter_date})
                        )
                    if filter_type == '1':
                        studies = studies.filter(
                            Q(**{field+'__lt': filter_date})
                        )
                    if filter_type == '2':
                        studies = studies.filter(
                            Q(**{field + '__gt': filter_date})
                        )
        else:
            search_text = request.GET.get(field)
            if search_text:
                studies = studies.filter(
                    Q(**{field + '__icontains': search_text})
                )
            filter_text = request.GET.get(field+'filter')
            print(filter_text)
            if filter_text:
                filter_type = request.GET.get(field+'filtertype')
                print(field)
                print(filter_type)
                if filter_type == '0':
                    studies = studies.filter(
                        Q(**{field + '__iexact': filter_text})
                    )
                if filter_type == '1':
                    studies = studies.exclude(Q(**{field + '__iexact': filter_text}))
                if filter_type == '2':
                    studies = studies.filter(
                        Q(**{field + '__startswith': filter_text})
                    )
                if filter_type == '3':
                    studies = studies.filter(
                        Q(**{field + '__endswith': filter_text})
                    )
                if filter_type == '4':
                    studies = studies.exclude(Q(**{field + '__icontains': filter_text}))

    total_records = studies.count()

    studies = studies.order_by(order_field)[start:start + per_page]

    return_items = list(
        studies.values('patient_fio', 'patient_birthdate', 'study_uid', 'study_date', 'study_modality__name'))

    return JsonResponse({
        'data': return_items,
        'recordsTotal': total_records,
        'recordsFiltered': total_records,
    }, safe=False)
