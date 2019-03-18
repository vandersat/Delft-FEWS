Delft-Fews/vds_fews_api_download.py
===================================

Python script to connect VanderSat data/API to Delft-FEWS


Usage:

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



Configuration
-------------

The configuration of this script is put in an .ini file.  An example
is given below:


::

    [API]
    # products = SM-SHORT-100,SM_C1N_100,INU-CLASSES-10,INU-RGB-10
    products = SM-SHORT-100,SM_C1N_100
    lat_min = 51.29971080556154
    lat_max = 51.865468048540635
    lon_max = 6.107025146484376
    lon_min = 5.037231445312501
    runinfofile = runinfo.xml
    date=2018-03-04

    user = username
    passwd = password


    # Do not change the items below unless you have a very good reason
    server = maps.vandersat.com/api/v1/dam/get-area
    format = NETCDF
    level = 3
    metadata = false
    as_attachment = true


:products: The products attribute should contain a comma separated lists of
    products. In case you want to connect to new/other products this list
    must be updated.

:lat_min: Minimum latitude of the bounding box that you want to download
    data from.

:lat_max: Maximum latitude of the bounding box that you want to download
    data from.

:lon_max: Maximum longitude of the bounding box that you want to download
    data from.

:lon_min: Minimum longitude of the bounding box that you want to download
    data from.

:runinfofile: Name of the runinfo file that Delft-FEWS exports,
    normally runinfo.xml

:user: username of you account

:passwd: password of your account

The other attributes should normally NOT be changed. See
http://docs.vandersat.com fro more detaisl on the API and the
viewer.



Delft-Fews configuration
------------------------


General adapter
~~~~~~~~~~~~~~~

In this step the VDS data is downloaded (in netcdf format) from the
VDS servers.

::

    <?xml version="1.0" encoding="UTF-8"?>
    <generalAdapterRun xmlns="http://www.wldelft.nl/fews" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wldelft.nl/fews http://fews.wldelft.nl/schemas/version1.0/generalAdapterRun.xsd">
	<general>
		<rootDir>$REGION_HOME$/Import</rootDir>
		<workDir>$REGION_HOME$/Modules/VDS</workDir>
		<exportDir>%ROOT_DIR%</exportDir>
		<importDir>%ROOT_DIR%/VDS</importDir>
		<importIdMap>IdImportVDS</importIdMap>
		<dumpFileDir>$GA_DUMPFILEDIR$</dumpFileDir>
		<dumpDir>%ROOT_DIR%</dumpDir>
		<diagnosticFile>%WORK_DIR%/vds_api_download.xml</diagnosticFile>
		<convertDatum>true</convertDatum>
	</general>
        <activities>
          	<exportActivities>
	                          <exportRunFileActivity>
				                         <exportFile>runinfo.xml</exportFile>
                                  </exportRunFileActivity>
		</exportActivities>
		<executeActivities>
			<executeActivity>
				<description>Run VDS-API Download</description>
				<command>
					<executable>$REGION_HOME$/Modules/VDS/vds_api_download.bat</executable>
				</command>
				<arguments>
					<argument>-R</argument>
					<argument>%ROOT_DIR%/runinfo.xml</argument>
					<argument>-u</argument>
					<argument>username</argument>
					<argument>-p</argument>
					<argument>password</argument>
					<argument>-o</argument>
					<argument>%ROOT_DIR%/VDS</argument>
				</arguments>
				<timeOut>44200000</timeOut>
				<ignoreDiagnostics>false</ignoreDiagnostics>
			</executeActivity>
                </executeActivities>
	</activities>
    </generalAdapterRun>


Tiemseries import
~~~~~~~~~~~~~~~~~

In this step the netcdf data is read into the system

::

    <?xml version="1.0" encoding="UTF-8"?>
    <timeSeriesImportRun xmlns="http://www.wldelft.nl/fews" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wldelft.nl/fews http://fews.wldelft.nl/schemas/version1.0/timeSeriesImportRun.xsd">
	<import>
		<general>
			<importType>NetcdfGridDataset</importType>
			<folder>$IMPORT_FOLDER$/VDS</folder>
			<failedFolder>$IMPORT_FAILED_FOLDER$</failedFolder>
			<backupFolder>$IMPORT_BACKUP_FOLDER$</backupFolder>
			<!-- <relativeViewPeriod unit="hour" start="-6" end="0" startOverrulable="true" endOverrulable="false"/> -->
			<idMapId>IdImportVDS</idMapId>
			<unitConversionsId>ImportUnitConversions</unitConversionsId>
			<importTimeZone>
				<timeZoneOffset>+00:00</timeZoneOffset>
			</importTimeZone>
			<dataFeedId>VDS</dataFeedId>
		</general>
		<timeSeriesSet>
			<moduleInstanceId>Import_VDS_netcdf</moduleInstanceId>
			<valueType>grid</valueType>
			<parameterId>SM.obs</parameterId>
                        <qualifierId>C-Band</qualifierId>
			<locationId>VDS</locationId>
			<timeSeriesType>external historical</timeSeriesType>
			<timeStep unit="nonequidistant"/>
			<readWriteMode>add originals</readWriteMode>
		</timeSeriesSet>
		<timeSeriesSet>
			<moduleInstanceId>Import_VDS_netcdf</moduleInstanceId>
			<valueType>grid</valueType>
			<parameterId>SM.obs</parameterId>
                        <qualifierId>L-Band</qualifierId>
			<locationId>VDS</locationId>
			<timeSeriesType>external historical</timeSeriesType>
			<timeStep unit="nonequidistant"/>
			<readWriteMode>add originals</readWriteMode>
		</timeSeriesSet>
		<timeSeriesSet>
			<moduleInstanceId>Import_VDS_netcdf</moduleInstanceId>
			<valueType>grid</valueType>
			<parameterId>Ref.obs</parameterId>
                        <qualifierId>Band1</qualifierId>
			<locationId>VDSS1</locationId>
			<timeSeriesType>external historical</timeSeriesType>
			<timeStep unit="nonequidistant"/>
			<readWriteMode>add originals</readWriteMode>
		</timeSeriesSet>
                <timeSeriesSet>
			<moduleInstanceId>Import_VDS_netcdf</moduleInstanceId>
			<valueType>grid</valueType>
			<parameterId>Inu.obs</parameterId>
			<locationId>VDSS1</locationId>
			<timeSeriesType>external historical</timeSeriesType>
			<timeStep unit="nonequidistant"/>
			<readWriteMode>add originals</readWriteMode>
		</timeSeriesSet>
	</import>
    </timeSeriesImportRun>





