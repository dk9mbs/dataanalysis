#!/usr/bin/python3

#cat /home/dk9mbs/wsprspots-2019-02.csv | grep DK9MBS | ./import.py --hook "/bin/bash /tmp/hook.sh" -q 2> /tmp/test.log


import sys
from datetime import datetime
import argparse
import os
from pyhamtools import LookupLib, Callinfo
from pyhamtools.frequency import freq_to_band
from pyhamtools.consts import LookupConventions as const


my_lookuplib = LookupLib(lookuptype="countryfile")


class Reader:
    def __init__(self, file,inithook=False, linehook=False, verbose=False):
        self._file=file
        self.linehook=linehook
        self.inithook=inithook
        self.verbose=verbose
        
    def read(self):
        for line in self._file:
            line=line.replace('\r\n',"")
            line=line.replace('\n',"")
            line=line.replace('\r',"")
            values=line.split(",")

            wsprLine=WsprLine(line, self.linehook, self.verbose)
            newLine=wsprLine.getConvertedLine()

            if self.verbose:
                sys.stdout.write (newLine+"\n")


class WsprField:
    def __init__(self,name,value):
        self._value=value
        self._name=name

    def getName(self):
        return self._name

    def getValue(self):
        return self._value
    

class WsprLine:
    def __init__(self,line, linehook="", verbose=False):
        self._line=line
        self._fields={}
        self.linehook=linehook
        self.verbose=verbose
        
        values=self._line.split(",")

        reporter={'latitude': 0, 'ituz': 0, 'country': 'NA', 'cqz': 0, 'continent': 'NA', 'adif': 0, 'longitude': 0}
        callsign={'latitude': 0, 'ituz': 0, 'country': 'NA', 'cqz': 0, 'continent': 'NA', 'adif': 0, 'longitude': 0}
        band={'band': 0, 'mode': 'NA'}
        
        cic = Callinfo(my_lookuplib)
        try:
            reporter=cic.get_all(values[2])
            if self.verbose:
                sys.stderr.write ("Decoded reporter => "+values[2]+"\n")
        except:
            sys.stderr.write("Error decoding reporter => "+values[2]+"\n")

        try:
            callsign=cic.get_all(values[6])
            if self.verbose:
                sys.stderr.write ("Decoded callsign => "+values[6]+"\n")
        except:
            sys.stderr.write("Error decoding callsign => "+values[6]+"\n")

        try:
            band=freq_to_band(float(values[5])*1000)
        except:            
            sys.stderr.write("Error decoding freq => "+values[5]+"\n")

        self._fields[0]= WsprField('spotid',values[0])
        self._fields[1]= WsprField('timestamp',datetime.utcfromtimestamp(int(values[1])).strftime('%Y-%m-%d %H:%M:%S'))
        self._fields[2]= WsprField('reporter',values[2])
        self._fields[3]= WsprField('reportergrid',values[3])
        self._fields[4]= WsprField('snr',values[4])
        self._fields[5]= WsprField('freq',values[5])
        self._fields[6]= WsprField('callsign',values[6])
        self._fields[7]= WsprField('grid',values[7])
        self._fields[8]= WsprField('power',values[8])
        self._fields[9]= WsprField('drift',values[9])
        self._fields[10]= WsprField('distance',values[10])
        self._fields[11]= WsprField('azimuth',values[11])
        self._fields[12]= WsprField('band',band['band'] )
        self._fields[13]= WsprField('version',values[13])
        self._fields[14]= WsprField('code',values[14])
        self._fields[15]= WsprField('date',datetime.utcfromtimestamp(int(values[1])).strftime('%Y-%m-%d'))
        self._fields[16]= WsprField('time',datetime.utcfromtimestamp(int(values[1])).strftime('%H:%M:%S'))
        self._fields[17]= WsprField('reporter_latitude',reporter['latitude'])
        self._fields[18]= WsprField('reporter_longitude',reporter['longitude'])
        self._fields[19]= WsprField('reporter_ituz',reporter['ituz'])
        self._fields[20]= WsprField('reporter_country',reporter['country'])
        self._fields[21]= WsprField('reporter_cqz',reporter['cqz'])
        self._fields[22]= WsprField('reporter_continent',reporter['continent'])
        self._fields[23]= WsprField('reporter_adif',reporter['adif'])

        self._fields[24]= WsprField('callsign_latitude',callsign['latitude'])
        self._fields[25]= WsprField('callsign_longitude',callsign['longitude'])
        self._fields[26]= WsprField('callsign_ituz',callsign['ituz'])
        self._fields[27]= WsprField('callsign_country',callsign['country'])
        self._fields[28]= WsprField('callsign_cqz',callsign['cqz'])
        self._fields[29]= WsprField('callsign_continent',callsign['continent'])
        self._fields[30]= WsprField('callsign_adif',callsign['adif'])
        self._fields[31]= WsprField('bandmode',band['mode'] )
        
        if self.linehook:
            self._execHook()
        else:
            sys.stderr.write("no hook script defined!\n")

    def _execHook(self):
        for key in self._fields:
            var="WSPR_"+(self._fields[key].getName()).upper()
            os.environ[var] = str(self._fields[key].getValue())
            if self.verbose:
                sys.stderr.write(var+" => "+str(self._fields[key].getValue())+"\n")

        if self.verbose:
            sys.stderr.write("execute hook:"+self.linehook+"\n")
        os.system(self.linehook)

    def getConvertedLine(self):
        fields=""
        for key in self._fields:
            fields+=self._fields[key].getName()+","


        values=""
        for key in self._fields:
            values+=str(self._fields[key].getValue())+","

        return values

        

class HamBand:
    def __init__(self):
        self.test=""

    def getBandByFreq(self, freq):
        return "---"



def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    
    parser.add_argument("-f", "--file", dest="file",
                        help="WSPR Input File", metavar="FILE")
    parser.add_argument("-l", "--linehook", dest="linehook",
                        help="Hook for every Line", metavar="LINEHOOK")
    parser.add_argument("-i", "--inithook", dest="inithook",
                        help="Initial Hook", metavar="INITHOOK")

    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="verbose", default=True,
                        help="don't print status messages to stdout")



    args = parser.parse_args()
    if args.file:
        file=open(args.file,"r")
    else:
        file=sys.stdin

    #file=open("/home/dk9mbs/wsprspots-2019-03.csv","r")
    reader = Reader(file)
    reader.linehook=args.linehook
    reader.inithook=args.inithook
    reader.verbose=args.verbose
    reader.read()


main()
