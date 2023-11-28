import csv
import os

import genvcf


def test_generate_vcs():
  with open('kathy.lopez@warren.org.vcf','w') as f:
    f.write(genvcf.implement_vcf('Lopez', 'Kathy', 'Horticulturist, amenity', 'kathy.lopez@warren.org', '001-383-311-4585'))
  with open('kathy.lopez@warren.org.vcf', 'r') as f:
    vcard = f.read()
    assert """\nBEGIN:VCARD
VERSION:2.1
N:Lopez;Kathy
FN:Kathy Lopez
ORG:Authors, Inc.
TITLE:Horticulturist, amenity
TEL;WORK;VOICE:001-383-311-4585
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:kathy.lopez@warren.org
REV:20150922T195243Z
END:VCARD\n"""   ==    vcard
  os.unlink('kathy.lopez@warren.org.vcf')
  

   



