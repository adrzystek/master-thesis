#!/bin/bash

NumberOfProcesses=8

ProgramName=fib
BucketName=results-bucket

AllPublicDnsNames=`aws ec2 describe-instances --output text --query 'Reservations[*].Instances[*].[PublicDnsName, Tags[0].Value]' --filters 'Name=instance-type,Values=c4.xlarge' 'Name=instance-state-name,Values=running' | grep -v 'BUSY' | awk '{print $1}'`

AllInstanceIds=`aws ec2 describe-instances --output text --query 'Reservations[*].Instances[*].[InstanceId, Tags[0].Value]' --filters 'Name=instance-type,Values=c4.xlarge' 'Name=instance-state-name,Values=running' | grep -v 'BUSY' | awk '{print $1}'`

PublicDnsNamesArray=($AllPublicDnsNames)

InstanceIdsArray=($AllInstanceIds)

PublicDnsNames="${PublicDnsNamesArray[0]} ${PublicDnsNamesArray[1]} ${PublicDnsNamesArray[2]} ${PublicDnsNamesArray[3]} ${PublicDnsNamesArray[4]}"

InstanceIds="${InstanceIdsArray[0]} ${InstanceIdsArray[1]} ${InstanceIdsArray[2]} ${InstanceIdsArray[3]} ${InstanceIdsArray[4]}"


for InstanceId in $InstanceIds; do aws ec2 create-tags --resources $InstanceId --tags Key=WorkingState,Value=BUSY; done

for PublicDnsName in $PublicDnsNames
do
  sftp -oStrictHostKeyChecking=no -i key.pem ec2-user@$PublicDnsName << EOS
  put ${ProgramName}_run.py
  mkdir .aws
  cd ./.aws
  put ./.aws/config
  exit
EOS
done

for PublicDnsName in $PublicDnsNames; do ssh -oStrictHostKeyChecking=no -i key.pem ec2-user@$PublicDnsName 'for i in `seq 8`; do python fib_run.py & done' & done

sleep 1h

let "TargetNumberOfResults = 5*${NumberOfProcesses}"

while true
do
  NumberOfResults=`aws s3 ls s3://${BucketName}/results/ | grep "${ProgramName}_${NumberOfProcesses}_times" | wc -l`
  if [ $NumberOfResults -eq $TargetNumberOfResults ]; then break; else sleep 5m; fi

done

sleep 3m

for InstanceId in $InstanceIds; do aws ec2 terminate-instances --instance-ids $InstanceId & done

for InstanceId in $InstanceIds; do aws s3 ls s3://${BucketName}/${ProgramName}_$NumberOfProcesses/$InstanceId/ | awk '{print $4}' > ${ProgramName}_headers_${NumberOfProcesses}_$InstanceId.txt; done

for InstanceId in $InstanceIds; do aws s3 cp ${ProgramName}_headers_${NumberOfProcesses}_$InstanceId.txt s3://${BucketName}/results/${ProgramName}_headers_${NumberOfProcesses}_$InstanceId.txt; done
