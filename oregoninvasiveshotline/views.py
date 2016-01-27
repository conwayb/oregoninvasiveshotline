from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .reports.models import Report
from .reports.serializers import ReportSerializer


class HomeView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home.html'

    # These options are used in :meth:`get_reports` to fetch the latest
    # N reports. They're class-level options so it's easy to change how
    # many reports are fetched, how they're filtered, and how they're
    # ordered (could be useful in tests, for example).
    show_n_reports = 25
    order_reports_by = '-created_on'
    report_filters = {
        'is_public': True,
    }

    def get(self, request):
        reports = self.get_reports()
        serializer = ReportSerializer(reports, many=True)
        return Response({
            'reports': serializer.data,
        })

    def get_reports(self):
        """Get reports to show on home page.

        Configure which reports are shown using the ``show_n_reports``,
        ``order_reports_by``, and ``report_filters`` class attributes.

        """
        q = Report.objects.filter(**self.report_filters)
        q = q.order_by(self.order_reports_by)
        return q[:self.show_n_reports]
