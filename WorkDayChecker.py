import arrow
from sys import exit
from lxml import etree
import subprocess
from functional import seq



HOLIDAYS = {}

def nextMonday(date):
    if date.isoweekday == 6:
        next_monday = date.shift(days=+2)
    elif date.isoweekday == 7:
        next_monday = date.shift(days=+1)
    return next_monday



def dateGenerator(first=(2019,1,1), last=(2019,12,31)):
    date = arrow.get(*first)
    lastday = arrow.get(*last)
    while date <= lastday:
        yield date
        date = date.shift(days=+1)


def getXmlString(date):
    date = date.format("YYYYMMDD")
    cmd = f'''dbtools "select content from workday where workdate='{date}'"'''
    process = subprocess.Popen(cmd, stdin = subprocess.PIPE, 
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=10)
        if stderr:
            print(stderr)
            exit("Can't get data from database.")
        xmlstring = str(stdout.strip()[0:-2]).strip()
    except subprocess.TimeoutExpired:
        process.kill()
        exit("Execute cmd timeout.")
    return xmlstring


def checkXml(xmlstring, xsdstring):
    try:
        xml = etree.fromstring(xmlstring)
        xsd = etree.fromstring(xsdstring)
        schema = xsd.XMLSchema(xsd)
    except etree.XMLSyntaxError as e:
        print(f"Syntax error: \n{e}")
    except etree.XMLShemaParseError as e:
        print(xmlstring)
    return (xml, schema.validate(xml))

def checkWorkDay(date, xml):
    workdate = date.format("YYYYMMDD")
    weekday = date.isoweekday()
    rounds = xml.xpath("//round")
    for round in rounds:
        roundno = round.xpath("/round@no")
        endtime = round.xpath("/end")
        cleardate = round.xpath("/cleardate")
        clearround = round.xpath("/clearround")
        svclist = round.xpath("/svclist")
        exchgstate = round.xpath("/exchgstate")
        try:
            if HOLIDAYS.get(workdate):
                cleardate = HOLIDAYS.get(workdate)
                assert (roundno, endtime, cleardate,
                        clearround, svclist, exchgstate) in (
                                    ('1', '083000', cleardate, '1', '1100', '1'),
                                    ('2', '110000', cleardate, '1', '1100', '1'),
                                    ('3', '153000', cleardate, '1', '1100', '1')
                        )
                continue
            if weekday in (6, 7):
                cleardate = nextMonday(date).isoformat("YYYYMMDD")
                assert (roundno, endtime, cleardate,
                        clearround, svclist, exchgstate) in (
                                ('1', '083000', cleardate, '1', '1100', '1'),
                                ('2', '110000', cleardate, '1', '1100', '1'),
                                ('3', '153000', cleardate, '1', '1100', '1')
                        )
            elif weekday in list(range(1,6)):
                assert (roundno, endtime, cleardate,
                        clearround, svclist, exchgstate) in (
                                ('1', '083000', workdate, '1', '1100', '1'),
                                ('2', '110000', workdate, '2', '1100', '1'),
                                ('3', '153000', workdate, '3', '1100', '1')
                        )
        except AssertionError:
            return False
    return True


if __name__ == '__main__':
    xsdstring = None
    with open("xsd.xsd") as xsdfile:
        xsdstring = xsdfile.read()
    for date in dateGenerator():
        xmlstring = getXmlString(date)
        xml, status = checkXml(xmlstring, xsdstring)
        if not all(status, checkWorkDay(date, xml)):
            print(f"Error workdate: {date}.")











