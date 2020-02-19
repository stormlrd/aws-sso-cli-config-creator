# aws-sso-cli-config-creator
Are you using AWS CLI v2 with AWS SO
Sick and tired of having to run aws sso configure --profile myprofilename for each role you have?

Or perhaps sick of just copying and pasting and editing rolenames manually in the config?

This script will **scrape** your roles from AWS SSO and create a AWS CLI v2 config file for you.

# Usage:
1. Clone this repository
2. Open the source_config, tweak the configuration to your SSO and primary account/role then save it
3. Copy & paste the source_config contents into your .aws\config file
4. Login to AWS SSO using aws sso login --profile primary
5. execute the script using py create_config.py
6. Transfer contents of config.new into your .aws\config file

Enjoy a long life.

# Dependancies
The script relies on a couple of things:

1. That you have already logged into AWS SSO using aws sso login --profile primary.
2. That you have configured your source_config file before running it
3. The the inital primary role you've specific has permissions to read from AWS SSO using list_account_roles() & list_accounts()

The initial login to aws sso requires that you have set up at least one profile in your config file for the aws cli. refer to the usage instructions.

# TroubleShooting:
If you get this error:

	*botocore.errorfactory.UnauthorizedException: An error occurred (UnauthorizedException) when calling the ListAccounts operation: Session token not found or invalid*

do an aws sso login again. the token has expired. I tried to write a check for this but there is a bug in the timestamp that the AWS CLI v2 writes out.

# Further reading
Blog post at dunlop.geek.nz: 

boto3 sdk for sso: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sso.html

aws cli v2 sso configuration: https://docs.amazonaws.cn/en_us/cli/latest/userguide/cli-configure-sso.html

AWS CLI V2 announcement post: https://aws.amazon.com/blogs/developer/aws-cli-v2-is-now-generally-available/