import boto3
import json

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    
    all_volumes = ec2_client.describe_volumes()
    
    unattached_volumes = [v for v in all_volumes['Volumes'] if not v['Attachments']]
    non_encrypted_volumes = [v for v in all_volumes['Volumes'] if not v['Encrypted']]
    
    non_encrypted_snapshots = ec2_client.describe_snapshots(Filters=[{'Name': 'encrypted', 'Values': ['false']}])
    
    metrics = {
        "unattached_volumes_count": len(unattached_volumes),
        "non_encrypted_volumes_count": len(non_encrypted_volumes),
        "non_encrypted_snapshots_count": len(non_encrypted_snapshots['Snapshots']),
    }

    # Upload to S3
    s3_client = boto3.client('s3')
    s3_bucket = "slawomir-nowakowski-use-case-6"
    s3_key = "metrics_{}.json".format(context.aws_request_id)
    
    s3_client.put_object(Body=json.dumps(metrics), Bucket=s3_bucket, Key=s3_key)

    return {
        'statusCode': 200,
        'body': json.dumps(metrics)
    }
