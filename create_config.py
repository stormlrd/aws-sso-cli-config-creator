#!/usr/bin/python3
#######################################################################
# Name: aws-sso-carf
# Version:  0.01
# Author: Paul Dunlop
# Description:
#   skeleton python script that allows for cross account looping in
#   AWS where AWS SSO is used to federate access
#######################################################################

###################################
# Library Work
#--------------
# import AWS Python SDK
import boto3
# for folder testing import os library
import os
# for clear() import only system from os 
from os import system, name 
# get pathlib class from path library for use with home folder on all OSes
from pathlib import Path
#JSON library for the sso cached cred files
import json
# for expiration check
import datetime
import time
# for config file work
import configparser

###################################
# Setup variables
#--------------
version="0.01" # used in console output
home = str(Path.home()) # find the current users home folder on all OSes to get to .aws folder

###################################
# FUNCTIONS
###################################
#----------------------------------
# Function: clear()
# Purpose: clears the screen
# Arguments: None
#----------------------------------
def clear(): 
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

#----------------------------------
# Function: get_aws_account_list(
# Purpose: your code to run in aws per account. modify as you see fit
# Arguments:
#       accessTokenfound, the access token from the json file
#----------------------------------
def get_aws_account_list():
    client = boto3.client('sso')

    # get list of all accounts
    accounts = client.list_accounts(
        maxResults=999,
        accessToken=accessTokenfound
    )

    #print("Accounts:", accounts)
    return accounts


########################
# MAIN ROUTINE
########################
clear()
# print banner
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("aws-sso-cli-config v", version)
print("Author: Paul Dunlop")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Please Note:\n this script makes live calls againts AWS SSO.")
print(" you should have already logged in using:")
print("   aws sso login --profile primary")
print(" as this script requires the ./aws/sso/cached token files to be present")
print("")

# Check for cached creds folder
aws_sso_cache_folder = os.path.join(home,".aws","sso","cache")
test = os.path.isdir(aws_sso_cache_folder)
if test:
    #print("Found cached credentials folder.")
    pass
else:
    print("An aws cli sso folder was not found in your  .aws folder. please ensure you have configured and logged into aws sso before using.")
    exit()

# there should only be two files in this folder.
# so get the one thats not botocore-client-id-[region].json
found_flag = False
file_list = os.listdir(aws_sso_cache_folder)
for file in file_list:
    if file[0:18]== "botocore-client-id":
        pass
    else:
        cached_credentials_filename = file
        found_flag = True

# if a file is found then read in the accessToken from it else bomb out
if found_flag:
    # we've got a file to open
    #print("Found cached credentials file of: ", cached_credentials_filename)
    file_to_read = os.path.join(aws_sso_cache_folder, cached_credentials_filename)
    with open(file_to_read, 'r') as myfile:
        data=myfile.read()
    obj = json.loads(data)
    
    # do a check here for the expiration of the token or not. if not expired then read it and let the app work.
    # THERE IS A BUG IN THE SSO CACHED CREDS WHERE THE EXPIRATION DATE IS WRONG
    # The below code should work but as a result of the bug its broken
    # leaving the below in for the hell of it for now
    expiration = str(obj['expiresAt'])
    #print("SSO Token found ExpiresAt: ", expiration)
    expiration_inseconds = datetime.datetime.strptime(expiration, "%Y-%m-%dT%H:%M:%SUTC").timestamp()
    #print("Expiration:", expiration_inseconds)
    current_utcdatetime = datetime.datetime.utcnow()
    #print("Current UTC Time:", current_utcdatetime)
    current_utcdate_inseconds = datetime.datetime.utcnow().timestamp()
    #print("current time in seconds: ", current_utcdate_inseconds)
    #if current_utcdate_inseconds <= expiration_inseconds:
    #    print('current time is less than expiration time')
    #else:
    #    print('current time is greater than expiration time')

    expired_token = False # hardset flag for now
    accessTokenfound=str(obj['accessToken'])
else:
    #we've got no file to open! :(
    print("No cached credentials file found. Please ensure you use aws sso login --profile primary to login")
    exit()

if expired_token: # true = expired, must re-login
    print("Token has expired. Please use aws sso login --profile primary again.")
    exit()
else: # false = non expired, current session available to use
    print("Reading in your source settings from source_config to use in new config sections...")
    config = configparser.ConfigParser()
    config.read('source_config')
    sso_start_url = config.get("profile primary","sso_start_url")
    #print("sso_start_url found to use: ", sso_start_url)
    sso_region = config.get("profile primary","sso_region")
    #print("sso_region found to use: ", sso_region)
    sso_account_id = config.get("profile primary","sso_account_id")
    #print("sso_account_id found to use: ", sso_account_id)
    sso_role_name = config.get("profile primary","sso_role_name")
    #print("sso_role_name found to use: ", sso_role_name)
    region = config.get("profile primary","region")
    #print("region found to use: ", region)
    output = config.get("profile primary","output")
    #print("output found to use: ", output)

    print("Discovering accounts in AWS SSO...")
    accountList = get_aws_account_list()

    print("Discoverying roles in AWS SSO & creating config.new file...")
    client = boto3.client('sso')

    # for each account in our account list get the roles
    for account in accountList["accountList"]:
        #print("Role check for AccountId: ", account["accountId"])
        roles = client.list_account_roles(
            maxResults = 999,
            accessToken = accessTokenfound,
            accountId = account["accountId"]
        )
        temp_account_name = account["accountName"]
        for role in roles["roleList"]:
            temp_role_name = role["roleName"]
            temp_role_accountId = role["accountId"]
            section_name = "profile " + temp_account_name + "-" + temp_role_name
            config.add_section(section_name)
            config.set(section_name, 'sso_start_url', sso_start_url)
            config.set(section_name, 'sso_region', sso_region)
            config.set(section_name, 'sso_account_id', temp_role_accountId)
            config.set(section_name, 'sso_role_name', temp_role_name)
            config.set(section_name, 'region', region)
            config.set(section_name, 'output', output)
    if os.path.exists("config.new"):
        os.remove('config.new') # get rid of any pre-existing files
    with open('config.new', 'w') as configfile:
        config.write(configfile)
    print("\nFinished.\n\nconfig.new file has been created.")
