# SSG Test Task: AI Engineer

## Cloning the Repository and Switching to the dev Branch
>The `feature/ssg-test-task` branch has the code now. 

```commandline
>> git clone https://github.com/Hassibayub/saic-hassibayub.git
>> cd saic-hassibayub
>> git switch feature/ssg-test-task
```

## Install Docker on your machine
Follow the instructions on the [official Docker website](https://docs.docker.com/get-docker/).

## Run the Docker Container
```commandline
>> docker-compose up --build
>> docker-compose up --build -d # To run in detached mode
```

The application will be running on `http://localhost:8501/`.