![Code Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoieXE0aWNZKzVqK0liZGRKREFrQ1dpeTBzdEpuTFg3TmFsYzdyOXZjU05GNDQvNXVpY3RzRm5UbXM5Ry95U2tmY08vaWpQRCtSWURiOEJFb29xN2w3Z09RPSIsIml2UGFyYW1ldGVyU3BlYyI6InQyUVJ1aGFVOU43NTVOdkgiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)
# Contact Tracking
To view our project report go [here](./Documentation/CC_Project_Report.pdf).<br>
To view our project presentation go [here](./Documentation/CC_Project_Presentation.pdf).<br>
To view the tutorial of our research project (CI/CD for AWS Lambda) go [here](./research/tutorial/README.md).

### Folder Structure
- `aws_lambda` - for all serverless functions
- `frontend` - folder contains react codebase for our frontend
- `simulator` - Spark Simulation app with requirements and script to bootstrap EMR
- `terraform` - scripts for IaC
- `tests` - for our lambda and simulator modules

### Python project setup

Enforcing PEP8 standards:
A pre-commit hook configured automatically enforces the PEP-8 standards using yapf. 

To run unit tests
```shell script
pip install -r requirements.txt
pytest
```

### Frontend
The frontend is a ReactJS app and uses `npm` for dependency management and building.

```shell script
npm install
npm run-script start
npm run-script build
```

### Infrastructure setup
1. All IaC go into Terraform folder
2. We create build pipeline also using terraform
Note how variables are passed in
```shell script
terraform init
terraform apply -var="github_personal_token=1111aaaaa" -var="github_username=username"
```
Verify the plan shown and accept it with `yes`
