import json
import sys
import urllib.request
import wget
import subprocess
import os
import requests

version = sys.argv[1]
userXMLFile = sys.argv[2]
server_Id = sys.argv[3]

req = urllib.request.Request("https://ci-portal.seli.wh.rnd.internal.ericsson.com/api/deployment/deploymentTemplates/productSet/ENM/version/"+version)
response = urllib.request.urlopen(req)
data = response.read()
values = json.loads(data)

deploymentTemplatesVersion = values['deploymentTemplatesVersion']
print("The Deployment Template's Version: " + deploymentTemplatesVersion)

ddTemplateUrl = "https://arm1s11-eiffel004.eiffel.gic.ericsson.se:8443/nexus/content/repositories/releases/com/ericsson/oss/itpf/deployment/descriptions/ERICenmdeploymenttemplates_CXP9031758/" + deploymentTemplatesVersion + "/ERICenmdeploymenttemplates_CXP9031758-" + deploymentTemplatesVersion + ".rpm"
ddTemplateRpm = wget.download(ddTemplateUrl)
print("The deployment Template's RPM: " + ddTemplateRpm)

XMLFile = wget.download(userXMLFile)
XMLFileName = os.path.basename(XMLFile)
print("The DD File: " + XMLFileName)

sizename = XMLFileName.split("__")[0]
deployment = XMLFileName.split("_dd.xml")[0]

def run_command(command):
    """
    Executes a shell command and returns the output.

    Args:
       command (str): The command to execute.

    Returns:
        str: The output of the command.

    Raises:
        Exception: If the command fails.
    """
    p1 = subprocess.Popen(command,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)
    output, error = p1.communicate()
    if p1.returncode != 0:
        raise Exception(f"Command failed with error {error.decode('utf-8')}")
    return output.decode('utf-8')
def extract_rpm(rpm_file):
    """
    Extracts the contents of an RPM file.

    Args:
        rpm_file (str): The name of the RPM file.
    """
    command = f"rpm2cpio {rpm_file} | cpio -idm"
    run_command(command)

def get_versions(directory):
    """
    Finds the versions of deployment-support-tooling and defaultConfigurableEntities.

    Args:
        directory (str): The directory to search in.

    Returns:
        dict: A dictionary mapping keys to versions.
    """
    command = f"cd {directory}; grep dce-version */*.txt; grep dst-version */*.txt"
    output = run_command(command)

    versions={}
    lines=output.split("\n")

    for line in lines:
        parts = line.strip().split(":")
        if len(parts) == 2:
            filename, version = parts
            versionKey, versionValue = version.strip().split(" ")
            versions[versionKey.strip()] = versionValue.strip()
    print(versions)
    return versions

def generate_esf(size_name, deployment):
    command = f'''grep -oPz "(?s)External Scaling Factors\\].*?\\n\\K.*?(?=\\[)" ./ericsson/deploymentDescriptions/{size_name}/{deployment}_info.txt > ./{deployment}.esf; sed -i '/^$/d' ./{deployment}.esf'''
    print(f"The _info.txt file exists: {os.path.exists(f'./ericsson/deploymentDescriptions/{size_name}/{deployment}_info.txt')}")
    run_command(command)
#Usage
extract_rpm(ddTemplateRpm)
versions = get_versions("ericsson/deploymentDescriptions")
print(versions)
generate_esf(sizename, deployment)

def delete_last_line(filename):
    """
    Deletes the last line of a file if it does not contain any alphabetic characters.
    Prints the modified contents of the file to the console.

    Args:
        filename (str): The name of the file to modify.
    """
    with open(filename, 'r') as file:
        esf_contents = file.readlines()

    if not esf_contents[-1].strip().isalpha():
        esf_contents = esf_contents[:-1]

    with open(filename, 'w') as file:
        print("The contents of the .esf file: \n")
        file.writelines(esf_contents)

    for line in esf_contents:
        print(line, end='')

delete_last_line(f'./{deployment}.esf')
def get_server_info(serverID):
    """
    The function sends a GET request to the URL using the provided URL.
    If the request is successful, the function processes the JSON response to count the number of 'SVC' and 'SCP' nodes in the server data.

    If the request is not successful, the function prints an error message with the status code of the failed request.

    Args:
        serverID (str): The ID of the server to retrieve information from.
    """
    global number_of_svcs
    global number_of_scps

    dmt_server_info_url = f"https://ci-portal.seli.wh.rnd.internal.ericsson.com/api/deployment/{serverID}/vm/service/data/all/"
    server_contents = requests.get(dmt_server_info_url)

    if server_contents.status_code == 200:
        server_data = server_contents.json()
        blade_count = {"svc": set(), "scp": set()}

        for node in server_data:
            node_list = node.get("node_list")
            if "SVC" in node_list:
                blade_count['svc'].add(node_list)
            elif 'SCP' in node_list:
                blade_count['scp'].add(node_list)

        count_dict = {"svc": len(blade_count['svc']), "scp": len(blade_count['scp'])}
        number_of_svcs = count_dict['svc']
        number_of_scps = count_dict['scp']
        print(count_dict)
    else:
        print(f"Request to retrieve server contents failed with status code {server_contents.status_code}")


get_server_info(server_Id)
print(number_of_svcs)
print(number_of_scps)


def checkout_repo_version(repo_name, repo_version):
    """"
    The function moves into cloned repositories and checks out the relevant version of that cloned repository.

    If the reset is successful, a response log is printed to the console.

    Args:
        repo_nme: The name of the cloned repository
        repo_version: the stored version of the cloned repository
    """
    command = f"cd {repo_name} && git reset --hard {repo_name}-{repo_version}"
    try:
        run_command(command)
        print(f"Successfully reset {repo_name} to version {repo_version}")
    except Exception as e:
        print(f"{str(e)}. Error with resetting {repo_name} to version {repo_version}.")


#Usage of checkout_repo_version below
keys = list(versions.keys())
dstVersion = versions[keys[1]]
dceVersion = versions[keys[0]]
checkout_repo_version("deploymentDescriptions", deploymentTemplatesVersion)
checkout_repo_version("deployment-support-tooling", dstVersion)
checkout_repo_version("defaultConfigurableEntities", dceVersion)

def update_pom()

