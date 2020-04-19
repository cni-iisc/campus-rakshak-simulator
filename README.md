# Markov Simulator for modeling the spread of CoVID-19 in Indian demographics

This repository contains the source code for agent-based modeling the spread of CovID-19 at the scale of a large Indian city. This README document will help you familiarize yourself with the directory structure of the project and also provides the steps to run the simulator on your local machine.

The source code for the simulator is organized into four major directories.
The source code is still under development, and we shall be updating this README with more information as and when we have new modules developed.

```
|- .
  |- simulator/
  |- cpp-simulator/
  |- staticInst/
  |- visualizations/
  |- README.md
```


## Development

The development of the code is hosted on BitBucket.  If you would like to contribute to the development, please contact the corresponding author [Rajesh Sundaresan](mailto:rajeshs@iisc.ac.in).


## Running the code

### `StaticInst/` - Generates static files to instantiate a city based on Demographics data
The first stage of the simulator workflow is to generate static information required to instantiate a city. This is done by using the demographic data, information on the distribution and the number of households and the information of workplace distribution, school distribution and the employment statistics for a city. We look for the demographic data which contains data on the total population, number of children, the number of people who are employed, on a fine-grained geographic scope of ward or block of the city.

The README inside `staticInst/` provides more information about the data sources, directory structure which the script to generate static instantiation for a city. The scope of this README is to share with you the steps to get the script started for instantiating a city.

The script to instantiate a city is written in Python and the following are the steps to setup a running instance of the script.

#### Setting up the virtualenv
The first step will be to setup the virtualenv inside which we install the required python packages. Let us create a virtualenv named `edaDev`, you could replace it with a different name too,

`python3 -m venv edaDev` 

The above statement would create a new directory under `markov_simuls` with the path `markov_simuls/edaDev`. This directory will contain the python packages you install and also helps to create an isolated python environment without affecting your other packages. 
If you are comfortable with Anaconda, there are lot of guides to help you [setup a virtualenv](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/). The next step will be to activate the virtual environment `edaDev` and install the required packages there, which is done with the following commands:

```
source edaDev/bin/activate
```
```
pip install numpy scipy pandas geopandas shapely matplotlib
```

#### `staticInst/` - running the script to instantiate the city
After setting up the environment, we are ready to run the script to instantiate a city. We recommend starting with a toy model for Bangalore city for a population of 10,000 people with additional input parameters:

- average number of students per school: 300
- average number of people per workplace: 2

To instantiate a Bangalore city with the mentioned configurations run the command

```
python parse_and_instantiate.py bangalore 10000 300 2
```

This instantiates Bangalore where the population of 10,000 people are randomly distributed across the 198 wards of the city with each individual being assigned to a house, school, workplace and community centre based on their age, and commute distance.
The instantiated outputs are in the form of JSON files and will be available under `staticInst/data/bangalore`. 

In case, you are working with instantiating a new city, please create the data files similar to the ones found at `staticInst/data/base/bangalore/` directory.


The simulation listed in the paper use much larger populations (e.g., 12.4 million for Mumbai).  They are also generated with a different script (`newparse.py`) with slightly different parameters.  Run

```
python newparse.py -h
```

to see details of its options.

### `simulator/` and `cpp-simulator/` - running the simulation of CoVID-19 spread
The instantiated static files for Bangalore are now used to simulate the spread of the CoVID-19 infection spread based on a Markovian model. The design document contains detailed specifications about the model.  We provide two implementations of the simulator: in `JavaScript` and `C++14`, respectively.  The `JavaScript` implementation is intended for quickly visualizing smaller models in a web-based interface, while the `C++14` version is intended for batch procession of city models with populations of the order of 10 million.

Here we describe the process for running the `JavaScript` simulation.  The details for running the `C++14` version can be found in the README.md [file](cpp-simulator/README.md) in the `cpp-simulator` directory.

#### Running the `JavaScript` simulator

To set-up a running instance of the simulator, you would first need to switch to the directory `markov_simuls/simulator`
The simulator looks for the instantiated files for Bangalore in the simulator directory and thus copy the data files generated at `staticInst/data/bangalore` into `simulator/`.

Now, we also need to setup a web-server to serve the simulator on the web-browser. This is done using the SimpleHTTPServer script available by default in Python.

On Windows: `python -m http.server 8000`
On Linux:   `python -m SimpleHTTPServer 8000`

This sets up a web-server running locally on port 8000. This port number can changed to an available port number.
Once, the web-server is running, you can open your web browser and access `localhost:8000` or `127.0.0.1:8000` to access the simulator.

The simulator would first start by running the simulation on the background and outputs a `.csv` file which contains the number of people infected per ward.


### `visualizations/` - visualizing the infection spread over a period of time

This directory contains the code for web-based visualizations using the JavaScript simulator.

