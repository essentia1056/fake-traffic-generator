# Fake Traffic Generator

A serverless system on AWS that simulates privacy-focused web traffic on a schedule, logs each session to S3, and provides monitoring and cost controls.

## Prerequisites

* AWS CLI configured with appropriate permissions
* An S3 bucket for storing logs and deployment artifacts
* Basic familiarity with AWS Lambda, S3, and CloudFormation

## Repository Structure

```plaintext
fake-traffic-generator/
├── lambda/
│   └── fake_traffic.py
├── dashboards/
│   └── cloudwatch.json
├── template.yml
└── README.md
```

## Features

* **Scheduled traffic** using EventBridge (rate(7 minutes))
* **Privacy-focused URLs** (EFF, Tor Project, Monero, KrebsOnSecurity)
* **Session logging** to S3 (`s3://<YOUR_BUCKET>/logs/`)
* **CloudWatch dashboard** for Invocations, Errors, Duration, Billing
* **Cost control** via S3 lifecycle rule and AWS Budget alarms
* **Least-privilege IAM role** for Lambda

## One-Click Deployment

### 1. Zip and upload your code

**Replace `<YOUR_BUCKET>` with your actual S3 bucket name throughout these commands.**

```bash
zip lambda/fake_traffic.zip lambda/fake_traffic.py
aws s3 cp lambda/fake_traffic.zip s3://<YOUR_BUCKET>/code/fake_traffic.zip
```

### 2. Deploy CloudFormation

See `template.yml` for the complete infrastructure definition.

```bash
aws cloudformation deploy \
  --template-file template.yml \
  --stack-name fake-traffic-stack \
  --parameter-overrides BucketName=<YOUR_BUCKET> \
  --capabilities CAPABILITY_IAM
```

## Manual Console Steps

### 1. Create an S3 bucket named `<YOUR_BUCKET>`
   * Block public access
   * Add a lifecycle rule on prefix `logs/` to expire after 30 days

### 2. Create an IAM role for Lambda
   * Inline policy allowing `s3:PutObject` on `arn:aws:s3:::<YOUR_BUCKET>/logs/*`

### 3. Create a Lambda function
   * Runtime: Python 3.11
   * Handler: `fake_traffic.lambda_handler`
   * Role: the IAM role above
   * Environment variable: `LOG_BUCKET=<YOUR_BUCKET>`
   * Paste code from `lambda/fake_traffic.py` into the inline editor
   * Timeout: 30 seconds, Memory: 256 MB

### 4. Create an EventBridge rule
   * Schedule expression: `rate(7 minutes)`
   * Target: your Lambda function

### 5. Import the CloudWatch dashboard
   * Use the JSON in `dashboards/cloudwatch.json`

### 6. Set up an AWS Budget and a CloudWatch billing alarm

## Viewing Logs and Metrics

* **S3 logs**: browse the `logs/` folder in your bucket
* **Dashboard**: CloudWatch → Dashboards → fake-traffic-monitor

## Configuration

The Lambda function generates 2-4 random requests per invocation to the following URLs:

* https://www.eff.org/
* https://www.torproject.org/
* https://www.getmonero.org/
* https://krebsonsecurity.com/
* https://httpbin.org/get

Each session is logged as JSON with timestamp, URL, status code, and success/error information.

## Cost Considerations

*Estimates based on AWS Free Tier usage patterns:*

* **Lambda**: ~$0.20/month (7-minute intervals = ~6,000 invocations/month)
* **S3**: ~$0.50/month (assuming 30-day retention with lifecycle policy)
* **CloudWatch**: ~$0.30/month (metrics and dashboard)
* **Total estimated cost**: ~$1.00/month

*Actual costs may vary based on your AWS region, usage patterns, and account type.*

## Security Notes

* Uses least-privilege IAM permissions
* All traffic goes to legitimate privacy/security websites
* Logs are stored in your private S3 bucket
* No sensitive data is transmitted or stored

## Troubleshooting

**Lambda timeout errors**: Increase timeout from 30 to 60 seconds if needed

**S3 permission errors**: Verify the IAM role has `s3:PutObject` permission on your bucket's `logs/` prefix

**No traffic generated**: Check EventBridge rule is enabled and Lambda function is properly configured

## Next Steps

* Add Tor/I2P proxy support via a container image
* Increase user-agent variety and request patterns
* Integrate with additional AWS analytics or alerts
* Add geographic diversity with different AWS regions

## License

MIT License. See [LICENSE](LICENSE) for details.

**Warning**: This tool generates network traffic for privacy research and testing purposes. Ensure your usage complies with the terms of service of target websites and your organization's policies.