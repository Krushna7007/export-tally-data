# converter/urls.py

from django.urls import path
from .views import ConvertXMLtoXLSX,upload_xml_page

urlpatterns = [
    path('convert-xml-to-xlsx/', ConvertXMLtoXLSX.as_view(), name='convert-xml-to-xlsx'),
    path('upload-xml/', upload_xml_page, name='upload-xml-page'),
]
