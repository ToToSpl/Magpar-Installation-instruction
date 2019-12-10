# Magpar installation

Magpar is a finite element micromagnetic simulator. Its high efficiency and mpi implementation makes it a good option for your simulations. Unfortunately Magpar newest version is from 2010 which makes its installation hard for newcomers. This tutorial will show step by step installation on Ubuntu 16.04. It is advisable to have basic knowledge in Unix operating systems (how to navigate inside terminal etc.).

##  Instalation steps
Magpar installation is divided into three steps: downloading, setting and finally installing. During installation we will have to download these libraries:

 - Atlas 3.6.0 
 - Lapack 3.8.0
 - libpng 1.4.1
 - ParMetis 3.1.1
 - Petsc 3.1 p8
 - Sundials 2.3.0
 - Zlib 1.2.4
 - Mpi

In next steps I will provide links to these libraries but these might change, so you will have to find them by yourself.

## Magpar setting and downloading

First navigate to [Front Page of Magpar](http://www.magpar.net/) and download from download section source, documentation and examples (version 0.9). 
Open terminal and create work folder in home directory and download magpar.

    cd 
    mkdir work
    cd work
    wget http://www.magpar.net/static/magpar-0.9/download/magpar-0.9.tar.gz
    wget http://www.magpar.net/static/magpar-0.9/download/magpar-0.9_doc.tar.gz
    wget http://www.magpar.net/static/magpar-0.9/download/magpar-0.9_ex.tar.gz
Now unzip files

    tar xzvf magpar-0.9.tar.gz
    tar xzvf magpar-0.9_ex.tar.gz
    tar xzvf magpar-0.9_doc.tar.gz

 Go to documentation folder and launch firefox 
 

    firefox magpar-0.9/doc/html/install.html
    
   Webpage that should pop-out contains lots of information about certain steps of installation but some of them are outdated. If this instruction does not provide some information you can always search them on this webpage.

Now we will edit makefile.

    cd magpar-0.9/
    MAGPAR_HOME=$PWD; export MAGPAR_HOME
    PD=$MAGPAR_HOME/libs; export PD
    cd src/
    cp Makefile.in.defaults Makefile.in.$HOSTNAME
    gedit Makefile.in.$HOSTNAME
    
Text fille will pop up. You have to find and edit certain lines so they will look like this:

    MAGPAR_HOME = $(HOME)/work/magpar-0.9
    PETSC_VERSION = 3.1.0
    liblapack=lapack-3.8.0
    MPI_DIR     = /usr/bin
   Save and exit gedit. Now type:

    gedit Makefile.in
   Inside this file edit one line:
   
    PETSC_DIR   = $(PD)/petsc-3.1-p8
    
For now that is all about magpar.

## Downloading libraries 
In this section I provide download links to libraries we need. In the future some of these links might not work. Then you will have to find them on your own.
Go to libs folder and download all libraries we need:

    cd ../libs/
    wget https://sourceforge.net/projects/math-atlas/files/Stable/3.6.0/atlas3.6.0_Linux_PIIISSE1.tar.gz
    wget http://www.netlib.org/lapack/lapack-3.8.0.tar.gz
    wget https://sourceforge.net/projects/libpng/files/libpng14/older-releases/1.4.1/libpng-1.4.1.tar.gz
    wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/parmetis/OLD/ParMetis-3.1.1.tar.gz
    wget https://computing.llnl.gov/projects/sundials/download/sundials-2.3.0.tar.gz
    wget https://www.zlib.net/fossils/zlib-1.2.4.tar.gz
    wget http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-3.1-p8.tar.gz
   
   All libraries are now downloaded (without mpi but this will be done later). Time for their installation


## Installation of the libraries

### Atlas
From the previous step you should be in the libs folder. If so unzip Atlas library:

    cd $PD
    tar xzfv atlas3.6.0_Linux_PIIISSE1.tar.gz
    
 We will proceed with the installation the same as described in magpar documentation:

    ln -s Linux_* atlas
    lapacklib=$PD/atlas/lib/liblapack.a
    mv $lapacklib $lapacklib.atlas
### lapack
When installing lapack we will again proceed similarly as in the documentation, but we will use different make file. If you don't have installed gfortran it will be also installed.

    cd $PD
    sudo apt install gfortran
    FC=gfortran; TIMER=INT_ETIME
    tar xzvf lapack-3.8.0.tar.gz
    cd lapack-3.8.0
    cp make.inc.example make.inc
    make "FORTRAN=$FC" "LOADER=$FC" "TIMER=$TIMER"  "BLASLIB=$PD/atlas/lib/libf77blas.a $PD/atlas/lib/libatlas.a" "OPTS=-funroll-all-loops -O3 $OOPTS"  lapacklib
    

To check if everything was installed correctly type inside of the lapack folder:

    make lapack_testing
    
### mpi

For Ubuntu we can just used precompiled binaries from apt-get so we just have to type:

    sudo apt-get update
    sudo apt-get install mpi-default-dev
    sudo apt-get install mpd

### parametis

Again it will be done as in instruction, but we will change mpi that we will be using.

    cd $PD
    lib=ParMetis-3.1.1
    tar xzvf $lib.tar.gz
    cd $lib
    make "CC=mpicc" "LD=mpicc"
    # run tests (optional)
    cd Graphs
    mpirun -np 4 ptest rotor.graph
    # more tests in ParMetis-3.1.1/INSTALL
### sundials

Same as in documentation but we will change mpi in the configure program

	cd $PD
	lib=sundials-2.3.0
	tar xzvf $lib.tar.gz
	cd $lib
	CFLAGS="-O3"; export CFLAGS
	./configure --prefix=$PD/$lib --with-mpi-incldir=/usr/bin
	make && make -i install

It is always worth a while to check if the configure program didn't print out any mistakes . If magpar compilation will fail check if in lib folder inside sundials if parallel files are in. If not you may have a problem with mpi.

### Petsc

Petsc is using python script for installation. This script has to be edited by us, but firstly prepare library:

    sudo apt-get install libblas-dev liblapack-dev
    cd $PD
    lib=petsc-3.1-p8
    tar xzvf $lib.tar.gz
    cd $lib
    PETSC_DIR=$PD/$lib; export PETSC_DIR
    PETSC_ARCH=PETSc-config-magpar; export PETSC_ARCH
    PRECISION=double; export PRECISION
    ATLAS_DIR=$PD/Linux_PIIISSE1/lib; export ATLAS_DIR
    cp $MAGPAR_HOME/src/PETSc-config-magpar.py $PETSC_DIR/config/

Now open this script inside gedit (or different text editor)

    gedit config/PETSc-config-magpar.py
In the file find correct lines of code (they have the same beginning) and replace them with these:

    '--LIBS=',
    '--with-mpi-dir=/usr/bin',
  Also comment (by writing # at the beginning) these lines:
  

    #'-COPTFLAGS='+os.environ['OPTFLAGS'],
    #'-CXXOPTFLAGS='+os.environ['OPTFLAGS'],
    #'-FOPTFLAGS='+os.environ['OPTFLAGS'],
  Save changes and exit gedit. Finally run the script and compile:
  

    ./config/PETSc-config-magpar.py
    #run command that will popout and the end of running script
    make PETSC_DIR=$PD/petsc-3.1-p8 PETSC_ARCH=PETSc-config-magpar all
    # run tests (optional)
    make PETSC_DIR=$PD/petsc-3.1-p8 PETSC_ARCH=PETSc-config-magpar test

  
### Zlib

Zlib installation is also similar to documentation but we will run configure program.

    cd $PD
    lib=zlib-1.2.4
    tar xzvf $lib.tar.gz
    ln -s $lib zlib
    cd $lib
    ./configure
    make CFLAGS="-O -fPIC" && make test

 ### Libpng 
 Libpng is done totaly as in documentation, but we use newer version of the library.

    cd $PD
    lib=libpng-1.4.1
    tar xzvf $lib.tar.gz
    ln -s $lib libpng
    cd $lib
    instdir=$PD/$lib
    ./configure --prefix=$instdir --enable-shared=no 2>&1 | tee configure.log
    CFLAGS="-I$PD/zlib"; export CFLAGS
    LDFLAGS="-L$PD/zlib"; export LDFLAGS
    cp scripts/makefile.linux Makefile
    make ZLIBLIB=../zlib ZLIBINC=../zlib && make test

All libraries has been installed! Finally we can compile Magpar.

## Magpar compilation

This one should be very simple, but you may encounter some compiling errors. If so try to look for error messages and using them find library that is not working. But let's hope that it will compile correctly!

    cd $MAGPAR_HOME/src
    make

 # Magpar testing 
 After successful installation it is time to try if the program is working. Fortunately Magpar is provided with many examples inside of magpar-examples folder. When we want to run some example we need to begin with two things. First copy magpar.exe from src folder, then lunch mpi (if it's not running yet). Let's try magpar on nanodot example.

Go to the nanodot example folder:

    cd $MAGPAR_HOME/magpar-examples/nanodot
    cp $MAGPAR_HOME/src/magpar.exe ./
    sudo mpd
    mpirun -np <number of cores of your machine> ./magpar.exe

Now the example should run! After it finishes you should see some additional files in the folder like the images of the simulation and so on. By using for example top command you can check if all cores of your machine are being used for performing simulation.

One important thing, every time you relaunch terminal window all the variables to the paths (like $PD or $MAGPAR_HOME) will be gone. You will have to add them again all use more convenient approach by use of local paths (again basic knowledge of Linux is very useful).

Happy physicsing!
