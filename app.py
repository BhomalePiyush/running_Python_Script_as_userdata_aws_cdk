#!/usr/bin/env python3
import os

import aws_cdk as cdk
# from multiuserdata.multiuserdata_stack import MultiuserdataStack
from Mystack.ec2_instance import EC2
from Mystack.loader_bucket import LoaderS3

env_dev = cdk.Environment(account="<account_number>", region="us-east-1")
app = cdk.App()
EC2(app, "MultiuserdataStack", env=env_dev)
LoaderS3(app, "dataloader", env=env_dev)
app.synth()
