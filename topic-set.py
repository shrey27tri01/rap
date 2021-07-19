#!/usr/bin/python3

import sys
import os
import csv
import string
import subprocess
import functools

def readContents(fileName):
  if(not os.path.isfile(fileName)):
    print(fileName + ": file does not exist.")
    raise FileNotExistsError(fileName)
  ifile  = open(fileName, "r")
  csvContents = csv.reader(ifile)
  trimmedContents = []
  for row in csvContents:
    trimmedRow = [cell for cell in row if cell !=  ""]
    if(len(trimmedRow) != 0):
      trimmedContents.append(trimmedRow)
    else:
      trimmedContents.append(None)
  return trimmedContents

def print_set(l):
  for e in l:
    print(e)

def add_unique(utopics, topic):
  found = False
  for ut in utopics:
    if(ut.lower() == topic.lower()):
      found = True
      break
  if(found is False):
    utopics.append(topic)

if __name__ == "__main__":
  contents = readContents("data/topics.csv")
  topics = [t for t, _ in contents]
#  ltopics = set([t.lower() for t in topics])

  utopics = []
  for t in topics:
    add_unique(utopics, t)
    
  print_set(utopics)

