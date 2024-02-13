# converter/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.renderers import JSONRenderer
import xml.etree.ElementTree as ET
import csv
from django.http import HttpResponse
from django.shortcuts import render


# views.py


def upload_xml_page(request):
    return render(request, 'upload.html')

class ConvertXMLtoXLSX(APIView):
    parser_classes = [MultiPartParser]
    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        xml_file = request.FILES.get('xml_file')

        if not xml_file or not xml_file.name.endswith('.xml'):
            return Response({'error': 'Please upload a valid XML file.'}, status=status.HTTP_400_BAD_REQUEST)

        try:

            # XML validation (optional)
            # Add your XML schema validation logic here
            headers = ["Date", "Transaction Type", "Vch No", "Ref No", "Reference Type", "Reference Date", "Debtor", "Reference Amount", "Amount", "Particulars", "Vch Type","Amount Verified"]
            rows = [headers]

            root = ET.parse(xml_file).getroot()
            voucher = root.findall('.//VOUCHER')

            for voucher in root.findall('.//VOUCHER'):
                
                date = voucher.find('DATE').text
                trans_type = 'Parent'
                vch_no = voucher.find('VOUCHERNUMBER').text
                ref_no = 'NA'
                ref_type = 'NA'
                ref_date = 'NA'
                ledgername = ''
                ref_amt = 'NA'
                amt     = 'NA'
                amt_verified = 'NO'

                debtor_element = voucher.find("LEDGERNAME") or voucher.find("PARTYLEDGERNAME")

                if debtor_element is None:
                    continue

                debtor = debtor_element.text
               

                allLedgerEntries =  voucher.findall(".//ALLLEDGERENTRIES.LIST") or voucher.findall(".//LEDGERENTRIES.LIST")
                
                for ledgerentrie in allLedgerEntries:

                    ledgername = ledgerentrie.find("LEDGERNAME").text
                        

                    billallocations = ledgerentrie.findall(".//BILLALLOCATIONS.LIST")
                    total_amount = 0
                    totalcalamt = float(ledgerentrie.find("AMOUNT").text) if ledgerentrie.find("AMOUNT") is not None else 0.0

                    for billallocation in billallocations:
                        child = billallocation.find("BILLTYPE")
                        other = billallocation.find("TRANSACTIONTYPE")

                        if child is not None:
                            child_type = child.text
                            trans_type = 'Child'
                            ref_no = billallocation.find("NAME").text
                            ref_type = billallocation.find("BILLTYPE").text
                            ref_date = ''

                            ref_amt = float(billallocation.find("AMOUNT").text)
                         
                            total_amount += ref_amt
                            rows.append([date,trans_type,vch_no,ref_no,ref_type,ref_date,ledgername,ref_amt,'NA',ledgername,'Receipt',amt_verified])
                            #print(f"Child Type: {date} {trans_type} {vch_no} {ref_no} {ref_type} {ref_date} {ledgername} {ref_amt} NA {ledgername} Receipt {amt_verified}")
                            ref_no = 'NA'
                            ref_type = 'NA'
                            ref_amt = 'NA'
                            amt = 'NA'
                            trans_type = 'Parent'


                    bankallocations = ledgerentrie.findall(".//BANKALLOCATIONS.LIST")

                    for bankallocation in bankallocations:

                        transaction_type = bankallocation.find("TRANSACTIONTYPE")
                        
                        if transaction_type is not None:
                            amount = bankallocation.find("AMOUNT").text
                            trans_type = 'Other'
                            rows.append([date,trans_type,vch_no,ref_no,ref_type,ref_date,ledgername,ref_amt,amount,ledgername,'Receipt',amt_verified])
                           # print(f"Other Type: {date} {trans_type} {vch_no} {ref_no} {ref_type} {ref_date} {ledgername} {ref_amt} {amount} {ledgername} Receipt {amt_verified}")
                
                if totalcalamt == total_amount:
                        amt_verified = 'YES'
                rows.append([date,trans_type,vch_no,ref_no,ref_type,ref_date,debtor,ref_amt,total_amount,debtor,'Receipt',amt_verified])
                #print(f"Parent Type: {date} {trans_type} {vch_no} {ref_no} {ref_date} {debtor} {ref_amt} {total_amount} {debtor} Receipt {amt_verified}")
            
           
            with open('source.csv', 'w') as csvfile:
                 csvwriter = csv.writer(csvfile)
                 csvwriter.writerows(rows)
            
            
            response = HttpResponse(content_type='application/csv')
            response['Content-Disposition'] = 'attachment; filename="ThePythonDjango.csv"'

            print(response)
            return HttpResponse(response)
              # Create the HttpResponse object with the appropriate CSV header.



        except ET.ParseError as e:
            return Response({'error': f'XML parsing error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
