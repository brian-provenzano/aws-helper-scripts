#!/usr/bin/python3
"""
validate-templates.py
---------------------
Validate a template or directory of templates using the AWS API (see limitations in docs) assumes yaml templates

Requirements:  
---------------------
You must have the boto3 python library loaded;  configured AWS profile

Usage:
---------------------
Please run validate-templates.py -h

TODO:
Possible extension to use as a git commit hook on pre-commit to check template validity

Author
------------------------
BJP - 11/21/18

"""
import argparse
from enum import Enum
import sys
import os
from pathlib import Path

# 3rd party modules needed
import boto3
from botocore.exceptions import ClientError, BotoCoreError, ValidationError

def main():
    parser = argparse.ArgumentParser(prog="validate-templates.py", description="Validate a template or directory of templates assumes yaml cloudformation format")
    #-group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--template", help="Validate this template")
    group.add_argument("-d", "--directory", help="Validate all templates in this directory - including all subdirectories")
    #-optional
    parser.add_argument("-p", "--profile", help="Provide your AWS profile name for the connection (optional - if not provided will attempt to use 'default' profile.")
    parser.add_argument("-v", "--version", action="version", version="1.0")
    args = parser.parse_args()

    try:
        if args.profile is not None:
            client= authenticate("cloudformation",args.profile)
        else:
            client = authenticate("cloudformation")

        validate(client,args.template,args.directory)

    except Exception as e:
        print_message(MessageType.ERROR,"Error occurred [{0}] ".format(type(e).__name__),e)


def authenticate(aws_resource: str, profile: str ="default"):
    ''' authenticate to AWS using boto3 session '''
    try:
        session = boto3.Session(profile_name=profile)
        client = session.client(aws_resource)
        print_message(MessageType.INFO,"Using AWS profile [ {0} ] to validate template(s)".format(profile))
        return client
    except ClientError:
        raise 
    except BotoCoreError:
        #boto3 / botocore exceptions are slim; this is the catchall :(
        raise


def validate(client,template=None,directory=None):
    ''' validate cloudformation template using boto api '''
    try:
        if template:
            path = "{0}/{1}".format(os.getcwd(),template)
            contents = ""
            with open(path,"r") as template_file:
                contents = template_file.read()
            client.validate_template(TemplateBody=contents)
            print_message(MessageType.INFO,"Template [{0}] Passed Validation!".format(template),None,False)

        if directory:
            for template in Path(directory).glob('*.yaml'):
                try:
                    path = "{0}/{1}".format(os.getcwd(),template)
                    contents = ""
                    if(template.stat().st_size >= 51200):
                        raise ValueError("Size of template is too large to validate (51,200 bytes) via AWS API")
                    with open(path,"r") as template_file:
                        contents = template_file.read()
                    client.validate_template(TemplateBody=contents)
                    print_message(MessageType.INFO,"Template [{0}] Passed Validation!".format(template),None,False)
                except ClientError as ce:
                    print_message(MessageType.ERROR,"Template [{0}] - Error occurred [{1}] ".format(template,type(ce).__name__),ce,False)
                    continue
                except ValueError as ve:
                    print_message(MessageType.ERROR,"Template [{0}] - Error occurred [{1}] ".format(template,type(ve).__name__),ve,False)
                    continue

    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except ClientError:
        raise 
    except BotoCoreError:
        #boto3 / botocore exceptions are slim; this is the catchall :(
        raise


def print_message(message_type,friendly_message,detail_message=None,show_message_type=True):
    """ prints messages in format we want """
    if message_type == message_type.DEBUG:
        color = fg.YELLOW
        coloroff = style.RESET_ALL
    elif message_type == message_type.INFO:
        color = fg.GREEN
        coloroff = style.RESET_ALL
    elif message_type == message_type.WARNING:
        color = fg.YELLOW
        coloroff = style.RESET_ALL
    elif message_type == message_type.ERROR:
        color = fg.RED
        coloroff = style.RESET_ALL
    else:
        color = ""
        coloroff = ""
    if not show_message_type:
        if detail_message == None:
            print("{1}{0}{2}".format(friendly_message,color,coloroff))
        else:
            print("{2}{0} - More Details : {1}{3}".format(friendly_message,detail_message,color,coloroff))
    else:
        if detail_message == None:
            print("{2}[{0}] - {1}{3}".format(str(message_type.name),friendly_message,color,coloroff))
        else:
            print("{3}[{0}] - {1} - More Details : {2}{4}".format(str(message_type.name),friendly_message,detail_message,color,coloroff))


class MessageType(Enum):
    """ Message type enumeration"""
    INVALID = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


# Terminal color definitions - cheap and easy colors for this application
class fg:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    RESET   = '\033[39m'

class bg:
    BLACK   = '\033[40m'
    RED     = '\033[41m'
    GREEN   = '\033[42m'
    YELLOW  = '\033[43m'
    BLUE    = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN    = '\033[46m'
    WHITE   = '\033[47m'
    RESET   = '\033[49m'

class style:
    BRIGHT    = '\033[1m'
    DIM       = '\033[2m'
    NORMAL    = '\033[22m'
    RESET_ALL = '\033[0m'


if __name__ == '__main__':
    main()