import os
from aws_cdk import (
    # Duration,
    Stack, aws_ec2 as _ec2,
    aws_iam as _iam

    # aws_sqs as sqs,)
)
from aws_cdk.aws_s3_assets import Asset
from constructs import Construct


dirname = os.path.dirname(__file__)


class EC2(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # initialize your vpc
        vpc = _ec2.Vpc.from_lookup(self,
                                   "importVPC",
                                   vpc_id="vpc-0efbae3722b5b51c9")

        #multipart_user_data = _ec2.MultipartUserData()
        #commands_user_data = _ec2.UserData.for_linux()
        # Read Bootstrap Script
        # with open('bootstrap_script(ex)/install_http.sh', mode="r") as file:
        #    user_data = file.read()


        # ec2 instance creation
        bot = _ec2.Instance(self, "Instance1",
                            instance_type=_ec2.InstanceType(instance_type_identifier="t2.micro"),
                            instance_name="multipart_experiment",
                            machine_image=_ec2.AmazonLinuxImage(
                                generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                            ),

                            #  block_devices=[_ec2.BlockDevice(
                            #      device_name="/dev/sdb",
                            #       volume=_ec2.BlockDeviceVolume.ebs(5)
                            #                                    )
                            #   ],
                            # user_data=_ec2.UserData.add,
                            #user_data=multipart_user_data,
                            key_name='ec2-access1',
                            vpc=vpc,
                            security_group=_ec2.SecurityGroup.from_security_group_id(self, "SG", "sg-01ed140b60852210c",
                                                                                     mutable=False
                                                                                     ),
                            vpc_subnets=_ec2.SubnetSelection(
                                subnet_type=_ec2.SubnetType.PUBLIC
                            )
                            )
        # add permissions to access services
        bot.role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonS3FullAccess"
            )
        )
        bot.role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonKinesisFullAccess"
            )
        )
        # Script in S3 as Asset
        # asset = Asset(self, "Asset", path="bootstrap_script(ex)/install_http.sh")
        asset = Asset(self, "Asset", path="bootstrap_script(ex)/install_http.sh")
        local_path=bot.user_data.add_s3_download_command(
                                                           bucket=asset.bucket,
                                                           bucket_key=asset.s3_object_key
                                                           )

        # Userdata executes script from S3
        bot.user_data.add_execute_file_command(
            file_path=local_path
        )
        #asset.grant_read(bot.role)
