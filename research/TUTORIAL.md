# CI / CD for AWS Lambda

## Table Of Contents

1. [What is CI and CD](#what-is-ci-and-cd)
2. [AWS services For CI/CD](#aws-services-for-cicd)
    1. Code Build
    2. Code Deploy
    3. Code Pipeline
3. [Problem Statement](#problem-statement)
4. [Create a Lambda](#create-a-lambda) 

***

## What is CI and CD
Continuous Integration is popular software development methodology which minimises the overhead for integrating
various features of a software project. <br>
Software integration, especially for big projects, is a mammoth task. Usually, developers work on separate
features in a software and then finally they integrate everything together to make single, functional software
package. Or at least that is how it used to be, before we could not scale this final step efficiently. 
The software community quickly realised that solving integration errors should be done right after a new piece of 
code, however small, is added to the codebase. This way, if a log of changes is maintained, as in the version
control system like GitHub, an error could be traced back to the exact change when it happened. <br>

Github flow is one of the common methodologies to do CI. 
![github_flow](github_flow.png)<br>
Usually a developer, when adding a new feature to a project follows the following steps under PR approach:
<ol>
<li>Download the updated the Master Branch in Github. This branch is the main codebase for a project
and should be deployable at all times.</li>
<li>Create and checkout a new branch. </li>
<li>Make changes to the code base. Add new code. </li>
<li>Build the project and do automatic unit testing on the local machine. </li>
<li>Commit the changes and push to the remote repository. </li>
<li>Create a Pull Request (PR) to merge this feature branch with the master branch. </li>
<li>At this point, the master branch would have changed since when this
feature branch was checked out. This could result in merge conflicts. Solve these conflicts. </li>
<li>Also other developers may have some comments on the code. Discuss and review. </li>
<li>Merge the feature branch into the master branch.</li>
<li>Build the test the master branch. Debug the errors. </li>
<li>Commit the changes to the master branch</li>
</ol>
Some good practices to employ in CI are as follows:
<ul>
<li>Maintain a Single Source Repository.</li>
<li>Automate the Build. </li>
<li>Make Your Build Self-Testing. </li>
<li>Everyone Commits To the Mainline Every Day. </li>
<li>Every Commit Should Build the Mainline on an Integration Machine</li>
<li>Keep the Build Fast. </li>
<li>Test in a Clone of the Production Environment. </li>
<li>Make it Easy for Anyone to Get the Latest Executable. </li>
<li>Everyone can see what's happening. </li>
<li>Automate Deployment. </li>
</ul>
For more information on the above, checkout the paper by Martin Fowler:
Fowler, Martin, and Matthew Foemmel. "Continuous integration." (2006).


</ul>


## AWS Services For CI/CD

***

## Problem Statement
We want to create a lambda function that will be tested and deployed if test pass.
1. A new commit reaches Github
2. Build pipeline will be triggered
3. Tests run
4. Artifacts will be created
5. Update Lambda use new code artifact

***

## Create a Lambda
First lets create a lambda function for use in this tutorial, note the intention of this tutorial is to understand the
importance of CI and CD and lambda is a tool we used to demonstrate this. The steps listed below closely mimics 
[Task 6.2: Serverless example](https://github.com/CCBDA-UPC/Assignments-2020/blob/master/Lab06.md#task-62-serverless-example).
For the purpose of this tutorial we have created a sample python function and a test.
First iteration of our lambda returns a JSON response.
```json
{"message": "hello user"}
```
Our end goal is to deploy a lambda that responds with the `hello ${username}` where username will be passed as a 
[query param](https://en.wikipedia.org/wiki/Query_string)

### Steps:
1. Contrary to [Task 6.2: Serverless example](https://github.com/CCBDA-UPC/Assignments-2020/blob/master/Lab06.md#task-62-serverless-example)
for lambda function code will be populated by a zip file in S3. This is one of the tenants of the CI/CD, make deployment
separate from the code artifact.
2. First we will create a bucket which will host our lambda code, remember buckets names have to be globally unique.
![S3 bucket creation](lambda-bucket_creation.png)
3. Clone our [tutorial repository](https://github.com/anantgupta04/CC-ResearchProject)
4. Create a zip file `hello_user.zip` containing `hello_user.py` 
Readers in *nix environments can run the below command to generate this zip
```shell script
zip hello_user.zip hello_user.py
```
5. Upload `hello_user.zip` into S3 bucket created in step 2.
![Zip uploaded](lambda-zip_uploaded.png)
This zip becomes the source of our lambda function that we will create in further steps.
6. Following steps in [Task 6.2: Serverless example](https://github.com/CCBDA-UPC/Assignments-2020/blob/master/Lab06.md#task-62-serverless-example)
create a lambda, refer to images belows to identify differing configurations.
![Lambda config](lambda-function_config.png)
![Lambda config](lambda-api_gateway_config.png)
7. Once lambda has been created, navigate to the `Function code` block and select `Code entry type` from `Code Entry Type`
dropdown and insert object URL to the zip file you had uploaded to S3 in step 5.
The object URL can be found in the overview tab of the zip file.
Be sure to change the handler info as given in the image below.
![Lambda use S3](lambda-s3_code_load.png)
8. Click on the tab API Gateway, as shown in the screen capture below, to obtain the API Endpoint URL.
![Lambda Endpoint URL](lambda-designer.png) 
Navigate to the URL and ensure you see the following JSON response.
```json
{"message": "hello user"}
```
With our lambda created we can now move to the next stage of our tutorial.

***