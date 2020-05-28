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

