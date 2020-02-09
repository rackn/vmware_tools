#!/bin/bash
# Used to get a machine into a state such that the API
# will return a 409
#
# To use this first make a workflow
# Add the stages "inventory" and "always-fails"
# Next create a dummy machine
#     drpcli machines create mike
#
# Set the machine to local bootenv and apply the
# workflow you just made to it.
#
# Next create a config file for the agent
#
#    drpcli machines show Name:mike|jq -r .Uuid > foo.conf
#    drpcli users token rocketskates ttl 3y | jq -r .Token >> foo.conf
#    $editor foo.conf
#
#    # Example foo.conf
#    [Config]
#    endpoint = https://drp.mrice.internal:8092/api/v3
#    token = 2OrpVPXkkate7wjxciVymq-MpwxEG1yDDqOeSIebguNpDFCOH4Phdp_6cE99jPZvXyFeVAh62Erwycv5q8CeLxwOQafr-s5uBsX4fZrY5lgDc2DNP3D_NnbrfERz7Llqd0GuH6LS1CBqX-w7bwHANksVheDOZQgYTKU6tyAqtVuSd1-oXQ-R6aGpPmyb225kOFS-pZmGjmLi4Xp78JLTvn3ciAxnaSa2HaKDysG11b_E6XsgEnjopdzbOauiV7PMost45CYMxB6DOaz7xdrHUu7jyiM3vSZ37b7m1SKCTXufM3o2uKi7TJ_oOQbUPiX9uatKja40E_POykuBFYipN0Ms9gMdmUvFsylwxS69lCW4wxlWB2XndgXiS57wqY2RyLsjHCmDm6smPIbli_3fF6Ve5trJRS4W2f6MqbhemvOJ7Hd8WihFKkrXiSNAPhFKmnQzvyNcSNzF6r06s9KN9u26wvedLnz5G0J9A5_WxCVmiYExkKwN2AF8N0AJnYy4s0XqqFDjxgYinXXAoZqm_meow_pPuknrWF1ctkt7MkIjh3r8QlW8QiaLzDTzI8mWZ9hWNwn1vWrcfo-iJdMaULYYIqWOmADmgz5Z7jC-whX9TqrC68WWrbFUOKHaKWnkpGfYkGq1bkKUNL_5olwlAjh11FsJ8TTd-nvmYzxzZhkCvhmc98Fi8wBVzNZ5U3p6t_Y2s3aK9DpAiJWYGhZPtxAaFeOQIhPjlo737X22kD6AWzYnVbsU0vHQOLw0umpQuOhGaK54_MlPIDeCSqkTqJoWRdQuxvN2Yr6ib5uZGpxN50-YoBWbq7ViQHS4OjvLB_XaLWpwXE2LSsSEyRG01mvZvPkYc8tTJa-eNTnMbptkiYldnuIZfDo=
#    machine_uuid = efc8bba7-0adc-4b89-8299-02e9fa49e239
# Place foo.conf in the same directory as the setup.py file. This makes sure it is available
# inside the container which we do in the next step
#
# Using the Dockerfile build and fire up an instance of the
# container and log into it, using a volume mount to share your
# drpy development env with the container.
#
#    docker run -it --rm -v /home/errr/programs/work/vmware_tools/drpy:/opt/rackn drpydev /bin/bash
#
# Next you want to install drpy into the container in
# development mode.
#
#    cd /opt/rackn
#    pip3 install -e .
#
# Next start the agent
#
#    agent -f foo.conf
#
# The inventory should run, but wont have any info, then the always fail should run.
# The agent should be in WaitRunnable at this point. From the docker host run this script
# (do not stop the agent). The agent should mark the CurrentJob as failed, then go into WaitRunnable,
# the machine is already runnable so it should go into runtask which should create a new job
# which should work. Without the proper fix in place drpy does not handle the 409 and gets stuck in a
# loop.

CJ=$(drpcli machines show Name:mike | jq .CurrentJob -r)
drpcli jobs update $CJ '{ "State":"running" }'
drpcli machines update Name:mike '{"Runnable": true}'
