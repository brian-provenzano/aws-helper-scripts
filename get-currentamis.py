#!/usr/bin/python3
"""
get-currentamis.py
-----------------------
Simple script returns the current (latest) AMI for specified region (optional) and description (required); other options available 
-----------------------

Usage:
-----------------------
get-currentamis.py <ami-desc>
<ami-desc> = "linux_amazon, linux_amazon2, etc"

TODOs - future features?

"""

import boto3
import argparse
from botocore.exceptions import ClientError, BotoCoreError
from enum import Enum

##########################################
#- Modify the options below as needed
##########################################

SUPPORTED_AMIS = "linux_amazon,linux_amazon2,linux_ubuntu1604,linux_ubuntu1804,linux_rhel75,linux_rhel76,windows_2016base,linux_centos7"

##########################################
#- END - Do not modify below here!!!
##########################################

def main():

    parser = argparse.ArgumentParser(prog="get-currentamis.py", \
            description="Returns the current (latest) AMI imageid specfied")
    #-required
    parser.add_argument("ami_description", type=str, \
            help="Specify {0} Either as a single value or comma seperated list of values".format(SUPPORTED_AMIS))
    #-optional
    parser.add_argument("-r", "--region", \
            help="AWS region for AMI.  If not specified, will use AWS profile default")
    #-informational args
    # parser.add_argument("-d", "--debug", action="store_true",
    #         help="Debug mode - show more informational messages for debugging")
    parser.add_argument("-v", "--version", action="version", version="1.1")
    args = parser.parse_args()
    ami_description = args.ami_description.strip()

    try:
        description_list = ami_description.split(',')
        
        if len(description_list) == 0:
            raise ValueError("You must provide a single ami_description or a comma seperated list of ami_descriptions")

        notallowedlist = [x for x in description_list if x not in SUPPORTED_AMIS]
        if len(notallowedlist) != 0:
            raise ValueError("You specified one of more AMI descriptions that are not allowed [{0}]".format(''.join(notallowedlist)))

        if args.region:
            client = authenticate("ec2",args.region.strip())
        else:
            client = authenticate("ec2")

        get_image(description_list, client)

    except Exception as e:
        print_message(message_type.ERROR,"Error occurred [{0}] ".format(type(e).__name__),e)


def authenticate(aws_resource, region=None):
    ''' authenticate to AWS using boto3 session '''
    try:
        if region != None:
            session = boto3.Session(profile_name="default", region_name=region)
        else:
            session = boto3.Session(profile_name="default")
            region = session.region_name
        client = session.client(aws_resource)
        print_message(message_type.INFO,"Using AWS profile [ default ] which is currently set to the region [ {0} ]".format(region))
        return client
    except ClientError:
        raise 
    except BotoCoreError:
        #boto3 / botocore exceptions are slim; this is the catchall :(
        raise 


def get_image(description_list, client):
    ''' get the AMI image and description requested '''
    try:
        owner = ""
        name = ""
        for description in description_list:
            
            if description == "linux_amazon":
                owner = "amazon"
                name = "amzn-ami-hvm-*-x86_64-gp2"
            elif description == "linux_amazon2":
                owner = "amazon"
                name = "amzn2-ami-hvm-2.0.*-x86_64-gp2"
            elif description == "linux_ubuntu1804":
                owner = "099720109477"
                name = "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"
            elif description == "linux_ubuntu1604":
                owner = "099720109477"
                name = "ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-*"
            elif description == "windows_2016base":
                owner = "amazon"
                name = "Windows_Server-2016-English-Full-Base*"
            elif description == "linux_rhel75":
                owner = "309956199498"
                name = "RHEL-7.5_HVM_GA*"
            elif description == "linux_rhel76":
                owner = "309956199498"
                name = "RHEL-7.6_HVM_GA*"
            elif description == "linux_centos7":
                owner = "679593333241"
                name = "CentOS Linux 7 x86_64 HVM*"
            

            response = client.describe_images(
                Owners=[owner], 
                Filters=[
                {'Name': 'name', 'Values': [name]},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'root-device-type', 'Values': ['ebs']},
                {'Name': 'state', 'Values': ['available']},
                ],
            )
            amis = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
            ami = amis[0]['ImageId']
            description = amis[0]['Description']

            print("[ {0} ] - {1}".format(ami,description))

    except ClientError:
        raise 
    except BotoCoreError:
        #boto3 / botocore exceptions are slim; this is the catchall :(
        raise 


def print_message(message_type,friendly_message,detail_message="None"):
    """ prints messages in format we want """
    if message_type == message_type.DEBUG:
        color = Foreground.YELLOW
        coloroff = Style.RESET_ALL
    elif message_type == message_type.INFO:
        color = Foreground.GREEN
        coloroff = Style.RESET_ALL
    elif message_type == message_type.WARNING:
        color = Foreground.YELLOW
        coloroff = Style.RESET_ALL
    elif message_type == message_type.ERROR:
        color = Foreground.RED
        coloroff = Style.RESET_ALL
    else:
        color = ""
        coloroff = ""
    if detail_message == "None":
        print("{3}[{0}] - {1}{4}".format(str(message_type.name),friendly_message,detail_message,color,coloroff))
    else:
        print("{3}[{0}] - {1} - More Details [{2}]{4}".format(str(message_type.name),friendly_message,detail_message,color,coloroff))


class message_type(Enum):
    """ Message type enumeration"""
    INVALID = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


# Terminal color definitions - cheap and easy colors for this application
class Foreground:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    RESET   = '\033[39m'

class Background:
    BLACK   = '\033[40m'
    RED     = '\033[41m'
    GREEN   = '\033[42m'
    YELLOW  = '\033[43m'
    BLUE    = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN    = '\033[46m'
    WHITE   = '\033[47m'
    RESET   = '\033[49m'

class Style:
    BRIGHT    = '\033[1m'
    DIM       = '\033[2m'
    NORMAL    = '\033[22m'
    RESET_ALL = '\033[0m'

if __name__ == '__main__':
    main()
