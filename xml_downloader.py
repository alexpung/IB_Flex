import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REQUEST_VERSION = '3'
XML_VERSION = '3'
INITIAL_WAIT = 5  # Waiting time for first attempt
RETRY = 7  # number of retry before aborting
RETRY_INCREMENT = 10  # amount of wait time increase for each failed attempt


def make_xml_request(token, report_number, version):
    """Step 1 : Request IB to generate the flex query file by giving a request with the token
        note that the server is not always up and sometimes it is down on Sat/Sun"""
    url_values = urllib.parse.urlencode({'t': token, 'q': report_number, 'v': version})
    base_url = 'https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest'
    full_url = base_url + '?' + url_values
    with urllib.request.urlopen(full_url) as xml_request_response:
        root = ET.fromstring(xml_request_response.read())
        status = root.find('Status').text
        print('XML request is {}'.format(status))
        if status == 'Success':
            return root
        else:
            print('ERROR: XML request is rejected.')
            exit(1)


def get_xml(base_url, reference_code, token, version):
    """Step 2: After the request is accepted, you need to wait until the file is ready to download."""
    xml_url_values = urllib.parse.urlencode({'q': reference_code, 't': token, 'v': version})
    xml_full_url = base_url + '?' + xml_url_values
    retry = 0
    while retry < RETRY:
        timer = retry * RETRY_INCREMENT + INITIAL_WAIT
        print('Waiting {} seconds before fetching XML'.format(timer))
        time.sleep(timer)
        with urllib.request.urlopen(xml_full_url) as xml_data:
            xml_report = ET.fromstring(xml_data.read())
            if xml_report[0].tag == 'FlexStatements':
                print('XML download is successful.')
                return xml_report
            elif xml_report.find('ErrorCode').text == '1019':  # statement generation in process, retry later
                print('XML is not yet ready.')
                retry += 1
            else:
                print('Error Code: {}'.format(xml_report.find('ErrorCode').text))
                print('Error Message: {}'.format(xml_report.find('ErrorMessage').text))
                exit(1)
    print('ERROR: XML request retry all failed.')
    exit(1)


def download_xml(token, report_number, filename='data.xml'):
    xml_reply = make_xml_request(token, report_number, REQUEST_VERSION)
    xml_result = get_xml(xml_reply.find('Url').text, xml_reply.find('ReferenceCode').text, token, XML_VERSION)
    tree = ET.ElementTree(xml_result)
    # the response is actually an xml file that you can write directly to a file
    with open(filename, 'wb') as f:
        tree.write(f)
    exit(0)
