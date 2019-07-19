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

