"""
Run the VanderSat API Download script

usage

::

    vds_api_download.py [-h][-d][-R runinfofile][-i inifile][-o outputdir]

    -h: print usage information
    -u: vds api username
    -p: vds api password
    -i: ini/config file
    -o: outputdir
    -l: loglevel [DEBUG, INFO, ERROR]
    -R: name of the delft-fews runinfo.xml file
    -d: disable certificate checking (USE WITH CAUTION)

"""

import requests
import getopt, sys, os
from xml.etree.ElementTree import *
from datetime import *
import logging
import ConfigParser




def log2xml(logfile,xmldiag):
    """
    Converts a wflow log file to a Delft-Fews XML diag file

    """

    trans = {'WARNING': '2', 'ERROR': '1', 'INFO': '3','DEBUG': '4', 'CRITICAL': '1', 'FATAL': '1'}
    if os.path.exists(logfile):
        with open(logfile, "r") as fi:
            lines = fi.readlines()

        with open(xmldiag, "w") as fo:
            fo.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            fo.write("<Diag xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \n")
            fo.write("xmlns=\"http://www.wldelft.nl/fews/PI\" xsi:schemaLocation=\"http://www.wldelft.nl/fews/PI \n")
            fo.write("http://fews.wldelft.nl/schemas/version1.0/pi-schemas/pi_diag.xsd\" version=\"1.2\">\n")
            for aline in lines:
                alineesc = aline.translate(None,"><&\"\'")
                lineparts = alineesc.strip().split(" - ")
                fo.write("<line level=\"" + trans[lineparts[3]] + "\" description=\"" + lineparts[4] + " [" + lineparts[0] + "]\"/>\n")
            fo.write("</Diag>\n")


def setlogger(logfilename,loggername, thelevel=logging.INFO):
    """
    Set-up the logging system and return a logger object. Exit if this fails
    """

    try:
        #create logger
        logger = logging.getLogger(loggername)
        if not isinstance(thelevel, int):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(thelevel)
        ch = logging.FileHandler(logfilename,mode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        #create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s")
        #add formatter to ch
        ch.setFormatter(formatter)
        console.setFormatter(formatter)
        #add ch to logger
        logger.addHandler(ch)
        logger.addHandler(console)
        logger.debug("File logging to " + logfilename)
        return logger
    except IOError:
        print "ERROR: Failed to initialize logger with logfile: " + logfilename
        sys.exit(2)



def configget(config,section,var,default):
    """

    Gets a string from a config file (.ini) and returns a default value if
    the key is not found. If the key is not found it also sets the value
    with the default in the config-file

    Input:
        - config - python ConfigParser object
        - section - section in the file
        - var - variable (key) to get
        - default - default string

    Returns:
        - string - either the value from the config file or the default value


    """
    Def = False
    try:
        ret = config.get(section,var)
    except:
        Def = True
        ret = default
        configset(config,section,var,default, overwrite=False)

    default = Def
    return ret


def configset(config,section,var,value, overwrite=False):
    """
    Sets a string in the in memory representation of the config object
    Deos NOT overwrite existing values if overwrite is set to False (default)

    Input:
        - config - python ConfigParser object
        - section - section in the file
        - var - variable (key) to set
        - value - the value to set
        - overwrite (optional, default is False)

    Returns:
        - nothing

    """

    if not config.has_section(section):
        config.add_section(section)
        config.set(section,var,value)
    else:
        if not config.has_option(section,var):
            config.set(section,var,value)
        else:
            if overwrite:
                config.set(section,var,value)


def configsection(config,section):
    """
    gets the list of keys in a section

    Input:
        - config
        - section

    Output:
        - list of keys in the section
    """
    try:
        ret = config.options(section)
    except:
        ret = []

    return ret

def iniFileSetUp(configfile,logger):
    """
    Reads .ini file and returns a config object.

    Input:
        - configfile - name of the configfile (.ini type)
        - logger

    Output:
        - python config object

    """

    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    if os.path.exists(configfile):
        config.read(configfile)
    else:
        logger.error("Cannot open ini file: " + configfile)
        sys.exit(1)

    return config

fewsNamespace="http://www.wldelft.nl/fews/PI"
def getTimeStepsfromRuninfo(xmlfile, timestepsecs):
    """
        Gets the number of  timesteps from the FEWS runinfo file.
    """
    if os.path.exists(xmlfile):
        with open(xmlfile, "r") as f:
            tree = parse(f)

        runinf = tree.getroot()
        sdate = runinf.find('.//{' + fewsNamespace + '}startDateTime')
        ttime = sdate.attrib['time']
        if len(ttime) == 12:  # Hack for milliseconds in testrunner runifo.xml...
            ttime = ttime.split('.')[0]

        edate = runinf.find('.//{' + fewsNamespace + '}endDateTime')
        sd = datetime.strptime(sdate.attrib['date'] + ttime, '%Y-%m-%d%H:%M:%S')
        ed = datetime.strptime(edate.attrib['date'] + edate.attrib['time'], '%Y-%m-%d%H:%M:%S')
        diff = ed - sd

        if timestepsecs < 86400:  # assume hours
            return (diff.seconds + diff.days * 86400) / timestepsecs + 1
        else:
            return diff.days + 1  # Should actually be + 1 but fews starts at 0!
    else:
        print(xmlfile + " does not exists.")
        return None


def getEndTimefromRuninfo(xmlfile):
    """
    Gets the endtime of the run from the FEWS runinfo file
    """
    if os.path.exists(xmlfile):
        with open(xmlfile, "r") as f:
            tree = parse(f)
        runinf = tree.getroot()
        edate = runinf.find('.//{' + fewsNamespace + '}endDateTime')
        ed = datetime.strptime(edate.attrib['date'] + edate.attrib['time'], '%Y-%m-%d%H:%M:%S')
    else:
        print(xmlfile + " does not exists.")
        ed = None

    return ed


def getStartTimefromRuninfo(xmlfile):
    """
    Gets the starttime from the FEWS runinfo file
    """
    if os.path.exists(xmlfile):
        with open(xmlfile, "r") as f:
            tree = parse(f)
        runinf = tree.getroot()
        edate = runinf.find('.//{' + fewsNamespace + '}startDateTime')
        ttime = edate.attrib['time']
        if len(ttime) == 12:  # Hack for millisecons in testrunner runinfo.xml...
            ttime = ttime.split('.')[0]
        ed = datetime.strptime(edate.attrib['date'] + ttime, '%Y-%m-%d%H:%M:%S')
        # ed = pa
    else:
        return None

    return ed

def usage(*args):
    sys.stdout = sys.stderr
    for msg in args: print msg
    print __doc__
    sys.exit(0)

def date_range(start, end, timestepsecs):
        r = int((end + timedelta(seconds=timestepsecs) - start).total_seconds() / timestepsecs)
        return [start + timedelta(seconds=(timestepsecs * i)) for i in range(r)]


def main(argv=None):
    products = ["SM-SHORT-100", "SM_C1N_100"]

    runinfofile = None
    inifile = 'vds_api_download.ini'
    loglevel = logging.INFO


    level = "3"
    metadata = "false"
    as_attachment = "true"
    cert_checking = True


    if argv is None:
        argv = sys.argv[1:]
        if len(argv) == 0:
            usage()
            return

    ########################################################################
    ## Process command-line options                                        #
    ########################################################################
    try:
        opts, args = getopt.getopt(argv, 'R:u:p:i:o:dl:')
    except getopt.error, msg:
        usage(msg)




    for o, a in opts:
        if o == '-i': inifile = a
        if o == '-R': runinfofile = a
        if o == '-h': usage()
        if o == '-d': cert_checking = False
        if o == '-l': exec "loglevel = logging." + a

    thelogger = setlogger('vds_api_download.log','vds',thelevel=loglevel)

    confile= iniFileSetUp(inifile, thelogger)

    lat_min = configget(confile,"API", 'lat_min', "51.29971080556154")
    lat_max = configget(confile,"API", 'lat_max', "51.865468048540635")
    lon_max = configget(confile,"API", 'lon_max', "6.107025146484376")
    lon_min = configget(confile,"API", 'lon_min', "5.037231445312501")
    runinfofile = configget(confile, "API", 'runinfofile', "runinfo.xml")
    server = configget(confile,"API", 'server', "maps.vandersat.com/api/v1/dam/get-area")
    oformat = configget(confile,"API", 'format', "NETCDF")
    user = configget(confile,"API", 'user', "demo")
    passwd = configget(confile,"API", 'passwd', "demos")
    thedate = configget(confile,"API", 'date', "2018-03-04")
    products_comma = configget(confile,"API", 'products', "SM-SHORT-100,SM_C1N_100")
    products=products_comma.split(",")
    outputdir = configget(confile,"API", 'outputdir', "")

    for o, a in opts:
        if o == '-u': user = a
        if o == '-p': passwd = a
        if o == '-o': outputdir = a

    if runinfofile is not None:
        startdate = getStartTimefromRuninfo(runinfofile)
        enddate = getEndTimefromRuninfo(runinfofile)
        if enddate is None or startdate is None:
            thelogger.error("Error in input dates")
            exit(1)
        drange = date_range(startdate,enddate,86400)
    else:
        drange = [datetime.strptime(thedate, '%Y-%m-%d')]


    if 'NETCDF' in oformat:
        myext = '.nc'
    else:
        myext = '.tif'

    for ddate in drange:
        thedate = str(datetime.date(ddate))
        thelogger.info('Processing date: ' +  thedate)
        for product in products:
            ofname = os.path.join(outputdir, product + "_" + thedate + myext)

            if os.path.exists(ofname):
                thelogger.info('Skipping file: ' + ofname)
            else:
                thelogger.info('Processing product: ' + product)
                getstr = "https://" + user + ":" + passwd + "@" + server + "?lat_max=" + lat_max \
                         + "&lat_min=" + lat_min + "&lon_max=" + lon_max + "&lon_min=" + lon_min + "&date=" + thedate \
                         + "&product=" + product + "&file_format=" + oformat + "&metadata=false&as_attachment=true"
                thelogger.debug(getstr)
                r = requests.get(getstr, verify=cert_checking)
                if r.status_code == 200:

                    thelogger.info('Writing file: ' + ofname)
                    with open(ofname, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                else:
                    thelogger.fatal("Error while trying to get data from api: " + str(r.status_code))

    log2xml('vds_api_download.log','vds_api_download.xml')


if __name__ == "__main__":
    main()
