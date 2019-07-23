Digital Rebar Python Agent Edition
-----------------------------------

Building
========

To build drpy you must use a machine other than an ESXi host since it does not have setuptools.

System Requirements:
    - Python 3.5.3
        - setuptools
        - virtualenv
        - pip
    - Linux/Mac OSX
        - Bash
    - Docker
        - https://hub.docker.com/r/lamw/vibauthor
    - Git
    - pyenv (optional but is nice for multiple versions of python)

Docker is needed to be able to package the build directory into a vib. The docker container that is used for vibauthor will not
work for building drpy because it runs python 2.6


Start by creating a virtualenv

.. code-block::

  mkdir ~/venvs
  virtualenv -p ~/.pyenv/versions/3.5.3/bin/python ~/venvs/drpy
  mkdir -p ~/code/rackn

Next activate the virtual environment and check the code out from git, and build it.

.. code-block::

  source ~/venvs/drpy/bin/activate
  git clone git@github.com:rackn/drpy ~/code/rackn
  cd ~/code/rackn/drpy
  ./build.sh ~/docker/share/drpy_build

The last command above does the build and sets the build directory. Once the build is complete the contents of our build directory
need to be placed on an ESXi server using a vib. This documentation will assume you already have docker set up and configured.

.. code-block::

  docker run -v ~/docker/share/drpy_build:/var/rackn -d --name=vibauthor lamw/vibauthor
  docker exec -it vibauthor /bin/bash


Keeping this container around is optional so if you dont want to keep it dont use the -d, I find it helpful to keep it around because SSH keys
but its easy enough to get the kes you want into the container..

Now from inside the container you need to check out the firewall vib project, then add the contents of `/var/rackn/*` to the vib build dir

.. code-block::

  git clone git@github.com:michaelrice/esxi-firewall-vib ~/
  cd esxi-firewall-vib
  mkdir -p stage/payloads/drpy/opt/rackn/drpy
  cp -a /var/rackn/* stage/payloads/drpy/opt/rackn/drpy
  vim stage/descriptor.xml

With the `descriptor.xml` file open you need to edit a couple of sections. First you need to bump the version number. Next you need to add the
new payload to the `payloads` section.

.. code-block::

  <payload name="drpy" type="vgz"></paload>



Save those changes and build the vib.

.. code-block::

  vibauthor -C -t stage -f -v /var/rackn/drpy-version.vib


Exit the docker container. Now you need to add the vib file to the ESXi server. During my testing
I was only ever successfully able to install the vib from a VMFS volume


.. code-block::

  scp ~docker/share/drpy_build/drpy-version.vib root@esxi:/vmfs/volumes/datastore1
  ssh root@esxi
  esxcli software vib install -v /vmfs/volumes/datastore1/drpy-version.vib -f


Once the install is complete you are ready to use the agent.


.. code-block::

  cd /opt/rackn/drpy
  python agent -f ./some_config.conf


You will need to create and provide `some_config.conf`


Example Config File
===================

.. code-block::

  [Config]
  endpoint = https://api.drp.local:8092/
  token = EdBk_k7R3S5Q5Prz6uxdahbFdjKQPG_GsWEv1SUfa1rnVy-BIYw6jJ5_qrQGpROfZuanTrqSf37kSOYXhVaMxzHV3RC5_7s9ysBUZRtTVJF2G72XqNDDqlbR9mVnjNxQEX8p1l8NoUZdQ6WbYAmlkDMEvZB22QfiybQNzy_-vceUdEyvsKEH1_Q2j4PIHzaYF-7ZlfqCOD3cIeeGZXQH2xhGTpOQyvidt2Z1Y2lKiAQyhuGLn0Tt119Ju9NSshkHwEhoLjCcM6L37yadMy8Q5EAiLmKra4FqIFE9VqxHJZWteYis1HyWs_0gTH7Arwi4pNovneSCN679SwUhz8OwSzLg9rtxeF2JDcIFDS7DgXZaKLV97wP8PFbn3yBU1VT38aWQvraUxnZYaO1kiCwBL24PC24mhXzsUk1I-8sJvlqOc18JfYymq7PbrMtwbAU1tzSLkQJWxGn5EA_9xo9wKW-_FjTQvlGukRQ7lCDhXD8Q2TGH33cpXEgvjfklQvtdrOKQ_sBU4WSht5dzUbjVs9NvNJJHyspwo3govV_4WrMUCrxjkNiC_rCBgtfw9uhmnkT35CTPVMU0MVKG3Mb2OfcI3Owwpdinuz_fipYsEuoyxXkPilUAc6VdJdFRX02oDfoBQS3FrmLkx0CcmPTuZ4r8SIPKn1tl7Za6Hpt3LCSlQlUc1-Iy6I_qUo5zBHGrySIYfWa3Y1Dkb2eV4Cadz0PnJmgbBTVFYDW0t8aLDoywOOsSUPLt6TlMfCcxHGhDdgJoVvbbaS7uymJjsjkHRYtJVlb0M3DJuVgntYjNRPxK7c5HqSD5SnyG2eVnpVH8-QLgPz_kOyJtW8Vl8nMP0zYEBpiitKgGx9e-JITzOo_-eKCJOUtO3dI=
  machine_uuid = e1dec675-9f43-40d6-b501-e4e481d66378
