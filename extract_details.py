import os
import json
import PyPDF2
import xlsxwriter
import shutil
import re

pregap = re.compile(r'(?P<cap>[(/A-Z])')
postgap = re.compile(r'(?P<punc>[,/])')
base = "/home/keshav/Desktop/PE/P2-Interview/interview-panel/data/Pravesh-2019-1"
collated = os.path.join(base, "collated")

EXTRACT_KEYS = ['App Id', 'Email', 'FirstName', 'LastName', 'Program', 'Status', 'Mobile', 'Gender', 'DateofBirth',
                'PrimaryDomain', 'ResearchArea(Preference1)', 'ResearchArea(Preference2)', 'OtherAreasofInterest',
                'SecondaryDomain', 'Files Copied']

CORRECTIONS = {
    'FirstName': 'First Name',
    'LastName': 'Last Name',
    'DateofBirth': 'DOB',
    'PrimaryDomain': 'Primary Domain',
    'ResearchArea(Preference1)': 'Research Area (Pref 1)',
    'ResearchArea(Preference2)': 'Research Area (Pref 2)',
    'OtherAreasofInterest': 'Other Areas of Interest',
    'SecondaryDomain': 'Secondary Domain',
    'PartTime': 'Part Time',
    'FullTime': 'Full Time',
    'MasterofSciencebyResearch': 'MS Research',
}

# args = ["/usr/bin/pdftotext", '-enc', 'UTF-8', '', '-']


def correct_field(key, val):
    if key in ['FirstName', 'LastName']:
        return val.title()
    if key == 'Email':
        return val.lower()
    if val in CORRECTIONS:
        return CORRECTIONS[val]
    if val[0] == ':':
        val = val[1:]
    return re.sub(postgap, r'\g<punc> ', re.sub(pregap, r' \g<cap>', val))


def fill_details(wsheet, rownum, program, domain, pdf_path):
    emailid = ''
    try:
        # args[3] = pdf_path
        # res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # output = res.stdout.decode('utf-8')
        # return len(output) > 100

        with open(pdf_path, 'rb') as file_object:
            pdf_reader = PyPDF2.PdfFileReader(file_object)
            pages = pdf_reader.numPages
            keys_to_be_extracted = EXTRACT_KEYS.copy()
            for page in range(pages):
                pdf_page = pdf_reader.getPage(page)
                page_text_list = pdf_page.extractText().split('\n')
                page_text_list = [word.strip() for word in page_text_list]
                # print(page_text_list)
                for i, key in enumerate(page_text_list):
                    try:
                        col = EXTRACT_KEYS.index(key)
                        if key in keys_to_be_extracted:
                            wsheet.write(rownum, col, correct_field(key, page_text_list[i+1]))
                            keys_to_be_extracted.remove(key)
                            if key == 'Email':
                                emailid = page_text_list[i+1]
                    except ValueError:
                        pass
            return True, emailid.strip()
    except:
        # failed += 1
        return False, emailid.strip()


def copy_files(src_dir, target_dir):
    for filename in os.listdir(src_dir):
        fpath = os.path.join(src_dir, filename)
        if os.path.isfile(fpath):
            shutil.copy(fpath, target_dir)


workbook_msphd = xlsxwriter.Workbook(os.path.join(collated, 'msphd_applications.xlsx'))
workbook_mscdt = xlsxwriter.Workbook(os.path.join(collated, 'mscdt_applications.xlsx'))

domains_msphd, domains_mscdt = dict(), dict()
for root, dirs, files in os.walk(collated):
    for fname in files:
        print ("fname = " + root + '/' + fname)
        if fname.endswith('_faculty.pdf') or fname.endswith('_candidate.pdf') or fname.endswith('_office.pdf'):
            fields = fname.split('_')
            if len(fields) > 2:
                print(fname)
                tag, appid = fields[0].split("-"), fields[2]
                program, domain = tag[0], tag[1]
                workbook, domains = ((workbook_mscdt, domains_mscdt,) if program == 'MSCDT' else
                                     (workbook_msphd, domains_msphd,))
                if domain not in domains:
                    sheet = workbook.add_worksheet(domain)
                    domains[domain] = {'sheet': sheet}
                    for i, title in enumerate(EXTRACT_KEYS):
                        title = CORRECTIONS.get(title, title)
                        sheet.write(0, i, title)

                this_domain = domains[domain]
                domain_sheet = this_domain['sheet']
                file_path = os.path.join(root, fname)
                row = this_domain[appid]['row'] if appid in this_domain else len(this_domain)
                filled, email = fill_details(domain_sheet, row, program, domain, file_path)
                if appid not in this_domain and filled:
                    domain_sheet.write(row, 0, appid)
                    this_domain[appid] = {'row': row, 'copied': False}

                if email != '' and not this_domain[appid]['copied']:
                    src_dir = os.path.join(base, 'docarchive', 'Candidates', email)
                    if os.path.exists(src_dir):
                        # copy_files(src_dir, root)
                        domain_sheet.write(row, (len(EXTRACT_KEYS)-1), 'Y')
                        this_domain[appid]['copied'] = True
                    else:
                        domain_sheet.write(row, 9, 'N')

workbook_msphd.close()
workbook_mscdt.close()

app_counts_msphd = {key: (len(info)-1) for key, info in domains_msphd.items()}
app_counts_mscdt = {key: (len(info)-1) for key, info in domains_mscdt.items()}
not_copied_msphd = [appid for key, info in domains_msphd.items() for appid, app_info in info.items()
                    if appid != 'sheet' and not app_info['copied']]
not_copied_mscdt = [appid for key, info in domains_mscdt.items() for appid, app_info in info.items()
                    if appid != 'sheet' and not app_info['copied']]
print('MS-Ph,D)')
print(json.dumps(app_counts_msphd, indent=4))
print('Total: %d' % sum(list(app_counts_msphd.values())))
print('Not copied Files For: %d Applications' % len(not_copied_msphd))
print(not_copied_msphd)
print()
print('M.Sc Digital Society')
print(json.dumps(app_counts_mscdt, indent=4))
print('Total: %d' % sum(list(app_counts_mscdt.values())))
print('Not copied Files For: %d Applications' % len(not_copied_mscdt))
print(not_copied_mscdt)
