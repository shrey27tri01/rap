#!/usr/bin/python

import os
import shutil
import subprocess
import PyPDF2
import csv
from PyPDF2 import PdfFileReader

##################################################################################
def read_contents(fileName):
  if(not os.path.isfile(fileName)):
    print(fileName + ": file does not exist.")
    # raise FileNotExistsError(fileName)
  ifile  = open(fileName, "r")
  csvContents = csv.reader(ifile)
  trimmedContents = []
  for row in csvContents:
    trimmedRow = [cell for cell in row if cell != ""]
    if(len(trimmedRow) != 0):
      trimmedContents.append(trimmedRow)
    else:
      trimmedContents.append(None)
  return trimmedContents
##################################################################################

##################################################################################
def copy_applications():
  base = "/home/keshav/Desktop/PE/P2-Interview/interview-panel/data"
  src  = base + "/Pravesh-2019-1"
  dest = base + "/all_applications"

  programs = [ "MS-CS", "MS-ITS", "MS-SE", "PHD-CS", "PHD-ITS", "PHD-NCS",
    "PHD-SE", "MS-DS",  "MS-NCS", "MS-VLSI", "PHD-DS", "PHD-MATH", "PHD-PHY",
    "PHD-VLSI", "MS-VLSI", "PHD-ITS", "PHD-PHY",  ]

  for root, dirs, files in os.walk(base):
    for fname in files:
      for progname in programs:
        if(fname.startswith(progname)):
          newfname = fname[len(progname + "_2019-1_"):]
          break
      if(fname.endswith("office.pdf")):
        newfname = newfname.replace("_office", "")
        print("copying ", fname, " to ", newfname)
        subprocess.call(["cp", root + "/" + fname, dest + "/" + newfname])
      elif(fname.endswith("candidate.pdf")):
        newfname = newfname.replace("_candidate", "")
        print("copying ", fname, " to ", newfname)
        subprocess.call(["cp", root + "/" + fname, dest + "/" + newfname])
      elif(fname.endswith("faculty.pdf")):
        newfname = newfname.replace("_faculty", "")
        print("copying ", fname, " to ", newfname)
        subprocess.call(["cp", root + "/" + fname, dest + "/" + newfname])
##################################################################################

##################################################################################
'''
  This procedure returns the text contents of one PDF file whose name is provided as
  parameter. 
'''
def text_extractor(path):
  all_text = ""
  with open(path, 'rb') as f:
    pdf = PdfFileReader(f)
    for i in range(pdf.getNumPages()):
      page = pdf.getPage(i)
      text = page.extractText().lower().replace("\-\n", "")
      text = text.replace("\n", "")
      all_text += text
      wrapped_text_list = [t.rstrip("\n") for t in text.replace("\-\n", "")]
  return all_text
##################################################################################

##################################################################################
'''
  This procedure translates PDF files in the given base directory to corresponding
  text files. Used in translating the PDF application files to text files.
'''
def pdf_to_text():
  ommitted_files = [ "421.pdf" ]
  base = "/home/keshav/Desktop/PE/P2-Interview/interview-panel/data/all_applications"
  files = os.listdir(base)
  for fname in files:
    if(fname in ommitted_files):
      continue
    print("Converting", fname, "...")
    text = text_extractor(base + "/" + fname)
    newfname = fname.replace("pdf", "txt")
    with open(base + "/" + newfname, 'w') as f:
      f.write(text)
##################################################################################

##################################################################################
'''
Inputs:
  contents: CSV table containing faculty data.
    column 0     - faculty name
    column 1 ... - Topics

  This procedure transforms the given CSV table into a dictionary.
  key  : faculty name
  value: set of topics
'''
def get_faculty_topics(contents):
  faculty = set(row[0] for row in contents)
  faculty_topics = {}
  for f in faculty:
    ftopics = set([row[1].lower()for row in contents if row[0] == f])
    faculty_topics[f] = ftopics
  return faculty_topics
##################################################################################

##################################################################################
def lookup(words, text):
  return set([w for w in words if w.lower().replace(" ", "") in text])

##################################################################################
'''
  This procedure returns a list of triples. Each triple contains three parts:
  - Faculty
  - Application
  - Overlapping Topics
  The topics set is created by finding the topics which occur in text.
'''
def match_fac_app(ft, app_id, text):
  fac_app = []
  for fac in ft:
    ots = lookup(ft[fac], text) # overlapping topics
    fac_app.append((fac, app_id, ots))
  return fac_app
##################################################################################

##################################################################################
'''
  This procedure returns a list of triples for all application files
  found in the base directory.
'''
def match_all_applications(ft):
  base = "data/all_applications/"
  files = [f for f in os.listdir(base) if f.endswith(".txt")]
  all_fao = []
  for fname in files:
    app_id = fname[:-4]
    with open(base + fname, "r") as fin:
      text = fin.read()
      fac_app = match_fac_app(ft, app_id, text)
      all_fao.extend(fac_app)
  return all_fao
##################################################################################

def print_dict(d):
  for k in d:
    if(d[k] is None):
      print(k + " : None")
    else:
      print(k + " : " + d[k])
##################################################################################

##################################################################################
'''
  This procedure returns a pair of the following:
  - A map from email IDs to application IDs
  - A list of application IDs for which no email IDs were matched.
'''
def map_emails_app_ids():
  base = "data/all_applications/"
  contents = read_contents("data/research-applications-may-2019.csv")
  email_ids = [row[1] for row in contents]
  print(email_ids)
  files = [f for f in os.listdir(base) if f.endswith(".txt")]
  appid_emailid = {}
  for fname in files:
    app_id = fname[:-4]
    with open(base + fname, "r") as fin:
      text = fin.read()
      email_id = None
      for eid in email_ids:
        if eid in text:
          email_id = eid
          break
      appid_emailid[app_id] = email_id
  no_email_appids = [aid for aid in appid_emailid if appid_emailid[aid] is None]
  for aid in no_email_appids:
    with open(base + aid + ".txt") as fin:
      text = fin.read()
    print(text + " : " + str(int(aid)))
#  print_dict(appid_emailid)
  emailid_appid = {}
  for aid in appid_emailid:
    eid = appid_emailid[aid]
    if(eid is not None):
      emailid_appid[eid] = aid
  print_dict(emailid_appid)
  return emailid_appid, no_email_appids

##################################################################################

##################################################################################
if __name__ == "__main__":
#  text_extractor("data/all_applications/MS-VLSI_2019-1_037_faculty.pdf")
#  copy_applications()
#  pdf_to_text()
#  text = text_extractor("data/all_applications/421.pdf")
#  print(text)

# Matching all applications - begin
#  topics = read_contents("data/topics.csv")
#  ft = get_faculty_topics(topics)
#  all_fao = match_all_applications(ft)
#  for f, a, ts in all_fao:
#    print(f + ", " + a + ", " + str(ts))
# Matching all applications - end

  map_emails_app_ids()
##################################################################################
