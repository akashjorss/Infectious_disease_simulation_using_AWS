# Introuction to Docker and Elastic Container Service (ECS)

## Environment
This tutoirial is being run on MacOS Catalina v10.15.3.

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

![](imgs/docker_ps.png)
