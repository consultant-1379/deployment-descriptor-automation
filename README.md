# Deployment Descriptor Automation
## About
This script is used to extract the version of deployment templates from a specific version of an ISO.
It also downloads the corresponding RPM file and extracts it to find the versions of `deployment-support-tooling` and `defaultConfigurableEntities`.
As we will be testing on a physical server, the script generates an "external scaling factors" file which will be used by the DST tool to generate the DD.
The script will set/check out relevant versions of `deploymentDescriptions`,`defaultConfigurableEntities` and `deployment-support-tooling` in git.
## Dependencies
- pyhton3
- urllib
- wget
- subprocess
- os
  -requests

## Functions
* `run_command(command: str) -> str`: Executes a shell command and returns the output.
* `extract_rpm(rpm_file:str)`: Extracts the contents of an RPM file.
* `get_versions(directory: str)->dict`: Finds the versions of the `deployment-support-tooling`
  and `defaultConfigurableEntities`.
* `generate_esf(size_name, deployment)`: Takes in name of file and file size from `DD_XML_File_Link`.
  Generates ESF file utilised by the DST tool to generate the DD for testing on a physical server.
* `get_server_info(serverID)`: Counts the number of blades (SVC and SCP).
* `checkout_repo_version(repo_name, repo_version)`: Moves into required repository and checks out relevant version for that repository.
## Usage
Run the following commands to use the deployment descriptor.
```bash
docker build -t <image-tag> .
# image-tag can be any value
```
```bash
docker run -it <image-tag> <sprint-number.ISO-sprint-number> <DD_XML_File_Link> <server_ID>
# Same image-tag from the build
# DD_XML_File_Link: Staging area file for current ISO installation.
# The server ID of the target server we are going to install on
```
### Example
```bash
docker build -t dd-automation .
```
```bash
docker run -it dd-automation 24.07.90 https://ci-portal.seli.wh.rnd.internal.ericsson.com/static/tmpUploadSnapshot//2024-04-24_13-13-01/medium__production_dualStack_dd.xml 322
# "24.07" is the sprint number, and ".90" is the ISO from that sprint number
# 322 is the server ID.
```

## Output
After running the commands, the console outputs the following;
```bash
The Deployment Template's Version: 2.40.1

The deployment Template's RPM: ERICenmdeploymenttemplates_CXP9031758-2.40.1.rpm

The DD File: https://ci-portal.seli.wh.rnd.internal.ericsson.com/static/tmpUploadSnapshot//2024-04-24_13-02-31/large__production_dualStack__1aut_dd.xml

Command success
Command success
{'dce-version': '2.42.1', 'dst-version': '1.65.4'}
Deployment: large__production_dualStack__1aut
The _info.txt file exists: True
Command success
# Below are the contents of the ESF file.
maxNumberLTECells=40000
numberScriptingSessions=100
numberElementManagerSessions=75
maxNumberTransportNodes=7500
enm_deployment_type=Large_ENM
numberOpsGuiSessions=20
maxCells=40000
maxNumberWCDMACells=2000
numberOpsNuiSessions=250
numberWinfiolCliUsers=183
numberWinfiolServerUsers=266
numberAmosUsers=300
geoMetro=0
#The number of blades: 
{'svc': 4, 'scp': 2}
#Below are the responses to checking out the relevant versions of the required repositories:
#At the moment, You will need to clone the 3 required repositories. This requirement will be removed
#once the project is integrated into jenkins. 
Successfully reset deploymentDescriptions to version 2.40.6
Successfully reset deployment-support-tooling to version 1.65.4
Successfully reset defaultConfigurableEntities to version 2.42.3
```
