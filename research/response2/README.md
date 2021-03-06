# Introuction to Docker and Elastic Container Service (ECS)

## Environment
This tutoirial is being run on MacOS Catalina v10.15.3.

## Running the Hello-World docker application.
As a first step, an account on docker hub is created and docker in installed on our machine. The docker installation is verified by running the hello-world docker command.

![](imgs/hello_world_docker.png)

### Q1: Describe where docker finds the image of hello-world?
When the command `docker run hello-world` is run, docker looks for the image `hello-world` in the local machine. If it cannot find the image, it pulls the latest image from the dockerhub library `library/hello-world:latest`. In our case, since it was the first time we ran the docker run command, it pulled the image from the dockerhub.

### Q2: What do you think happened when we call the function run?
When we call the `docker run` function, the docker takes the following steps:

1. The Docker client contacts the Docker daemon.
2. The Docker daemon pulls the "hello-world" image from the Docker Hub.
3. The Docker daemon creates a new container from that image which runs the
    executable that produces the message "Hello from Docker".
4. The Docker daemon streams the output to the Docker client, which sends it
    to the terminal.
    
### Useful Docker Commands
Some useful commands were run to get the familiarization with docker as suggested by the tutorial. The commands and their corresponding output are shown below.

`docker ps` - Shows all containers that are running

![](imgs/docker_ps.png)

Since there are no containers running, the output is empty


`docker ps -a` - Shows the history of containers

![](imgs/docker_ps_a.png)

`docker container prune` - Clears all the stopped containers

![](imgs/docker_prune.png)

After clearning the containers, `docker ps -a` reponse is also empty

![](imgs/docker_ps.png)



`docker images`- Lists all the images stored locally

![](imgs/docker_images.png)


`docker rmi [img ID]` - removes the image with [imgID].

The commands helped us familiarize with the common docker commands to get started with docker.

### Building a Docker Image
To build the docker image, following steps were taken according to the tutorial.

1. Clone the repo `https://github.com/prakhar1989/docker-curriculum.git`
2. cd to `docker-curriculum/flask-app`
3. Run the build command `docker build -t haroonrashid/catnip .`

![](imgs/docker_build.png)

4. The new image that we built can be seen by the `docker images` command whose output is shown below.

![](imgs/docker_images_after_build.png)

5. The docker image is run using `docker run -p 5000:5000 haroonrashid/catnip`

![](imgs/docker_run.png)

6. The flask app is accessed at `localhost:5000`. The port 5000 is exposed for the app in the dockerfile.

![](imgs/flask_app.png)

## Deploying Docker on ECS
This part of the tutorial uses multiple docker containers and deploys them on Elastic Container Service (ECS) provided by AWS.

The following steps are taken to build and run the docker image for the foodtrucks-web app.
1. Clone the repo provided by the tutorial's author `https://github.com/aristonhariantolim/cctutorial-foodtruck.git`
2. cd to `cctutorial-foodtruck` and build the docker by running `docker build -t haroonrashid235/foodtrucks-web .`
3. Once the docker is successfully built, it is run locally by using `docker run -p 5000:5000 haroonrashid/foodtrucks-web`
4. Finally docker is pushed to the dockerhub using `docker push haroonrashid235/foodtrucks-23b`

Next, `ecs-cli` is installed on the machine to access the Elastic Container service using the command line.

![](imgs/ecs_cli.png)

ECS profile is conifgured for the user's AWS acount, using the user's `access-key` and `secret-access-key`.  
`ecs-cli configure profile --profile-name ecs-foodtrucks --access-key $AWS_ACCESS_KEY_ID --secret-key $AWS_SECRET_ACCESS_KEY`

A key-pair is created that is used to access the ecs-cluster and run tasks on it.
![](imgs/key_pair.png)

Finally, the cluster is created using the follwing command.

`ecs-cli up --keypair ecs_test --capability-iam --size 1 --instance-type t2.medium`

### Q3: What do you think all the parameters mean?
`--keypair`: Specifies the name of an existing Amazon EC2 key pair to enable SSH access to the EC2 instances in your cluster
`capability-iam`: Acknowledges that this command may create IAM resources
`--size`: Specifies the number of instances to launch and register to the cluster.
`--instance-type`: Specifies the type of EC2 instance to launch.



**Note: There were some issues with the credentials from the ecs-cli and the cluster could not run from the cli. Instead we created the cluster using the AWS console whose process is given below.**

## Creating ECS cluster from the AWS console
AWS provides you with two options to run your containers.
1. Fargate (Network Only): A serverless infrastructure maintained by Amazon ECS i.e. not exactly server less but you do not need to take the pain of maintaining and scaling the server.
2. EC2: We can use Elastic Compute Cloud with ECS to get more control over the server on which your container would be running.

We chose fargate for this tutorial, because it is serverless whose advantages we are well aware of. The steps for creating a cluster and running container on the AWS ECS are given below:

1. We create a cluster by selecting Elastic Container Service from AWS service list, select Clusters and create.
![](imgs/create_cluster.png)

As we are using Fargate in this section the obvious choice is Network Only and proceed with creating a cluster by entering the name of the cluster and networking details.
![](imgs/cluster_created.png)

2. Once the cluster is created, we create a task that will be running on the cluster we just created. To create a task move to Task Definitions option on the ECS menu and create a task definition.
![](imgs/task_created.png)

3. Now, we add a container to the task definition. We use Docker hub’s URL as our image is deployed on docker hub.
![](imgs/add_container.png)

4. Once the container is added,run a new task by clicking on Run new Task and the following screen appears.
![](imgs/launch_task.png)

5. Submit the details by clicking on Run. You will be able to view your task listed under the Tasks tab on the cluster with a RUNNING status.
![](imgs/run_task.png)

6. You can click on the task and get the details of your running service. In the network section, you can see your public IP where you can see your service running. This is not a static IP and it changes if you restart your task. You can use Amazon ALB to assign an Elastic IP.
![](imgs/task_running.png)

Finally, the deployed app can be accessed using the static IP provided.
![](cctutorial-foodtruck/shot.png)
### Q4: Can you think of a good use case of using multiple Docker containers for your project?
A good use case of Docker is its use in multi-tenant applications, thereby avoiding major application rewrites. For example is to develop quick and easy multi-tenancy for an IoT application. Code bases for such multi-tenant applications are far more complicated, rigid and difficult to handle. Rearchitecting an application is not only time consuming, but also costs a lot of money. Using Docker, it can be very easy and inexpensive to create isolated environments for running multiple instances of app tiers for each tenant. 

### Q5: What is the most interesting thing you have learnt in this tutorial? What are the problems and how do you solve them?
Ans: The tutorial was very interesting. We learned about the containerization and how applications can be deployed in an isolated and light-weight environments as compared to the virtual machines. The tutorial also taks about deploying containers on AWS Elastic Container service which was a very useful learning experience.

We faced some problems in the deployment of container on ECS. First of all, using the ecs-cli, we faced credentials issues on the educate account as it was not able to validate the credentials provided. The issue was resolved by creating a cluster using AWS console and deploying a docker image on it using console. Since, the tutorial talked about cli way of deployment, we had to look for docker and ecs documentation to get the container on ecs working.

#### FEEDBACK:

Apart from the inline feedback we have given, the overall impression of this tutorial is that

1. The overall tutorial was good and well explained. It had good pointers to resources for installation of things like dockerhub and docker for all the three platforms.
2. The tutorial evolution was good, it started off with hello-world docker, then introduced some docker commands and build and run a docker locally.
3. The last part of the tutorial was to deploy a container on ECS. This part was a little difficult to follow, because app that was provided to containerize and run was a bit buggy and no information on how to resolve those errors was provided.
4. Finally, we had to look for resources outside the tutorial provided to deploy the container on ECS and get the application running. This part could have been improved and more detailed could have been provided.

Nevertheless, we appreciate the effort put by the authors for this tutorial.

**Grade**: 9.0
