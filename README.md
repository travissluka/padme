# PADMÉ

**P**lotting tools for **A**nalysis, **D**iagnostics, **M**onitoring, and
**E**valuation

API capable of automated plotting from various sources, including binnned
statistics from [BESPIN](https://github.com/travissluka/bespin)

## Installation

### 1. Get source code

``` console
> mkdir padme
> cd padme
> git clone git@github.com:travissluka/bespin.git
> git clone git@github.com:travissluka/padme.git
```

### 2. Install conda

Conda is preferable to setting up a python venv because some libraries such as GEOS are required, and are easier to get via conda if they are not already available on the machine. If you already have a conda environment installed that you want to use, you can skip this section.

```console
> wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
> bash Miniconda3-latest-Linux-x86_64.sh
(when asked: install to ./conda)
(when asked: "Do you wish the installer to init Miniconda?": no)
> source conda/bin/activate
```

### 3. Create `padme` conda environment

This will create a conda environment named `padme` with all the required dependencies. *(This might take a while!)*

```console
> conda env create -f padme/environment.yaml
```

### 4. Activate the conda environment

Now, and every time you open a new bash instance to run `bespin` or `padme` tools, you'll have to run:

```console
> source conda/bin/activate padme
```

### 5. Install PADME and BESPIN packages

The packages are installed in "editable" mode, meaning if you need to update a version of any given package you can simply do a `git pull` without having to re-install.

```console
> pip install -e bespin
> pip install -e padme
```

## Usage

For details on how to use the binning package, see [BESPIN](https://github.com/travissluka/bespin)

For details on how to use PADME, run 

```console
> padme --help
```