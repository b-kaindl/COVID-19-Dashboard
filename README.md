# COVID-19 Dashboard

## About This Project
**DISCLAIMER**: This project is part of Udacity's Data Scientist Nanodegree. The model shipped with this version of the project is to be understood as a proof of concept or, at most, a starting point for further model improvements. Please refer to official information and guidance provided by your local authorities concerning the COVID-19 pandemic rather than trusting some stranger on the internet and their private coding project.


The goal of this project is to train a Temporal Fusion Transformer (TFT) Model on data retrieved from [_Our World in Data_](https://github.com/owid/covid-19-data/tree/master/public/data) and to provide an interface to access predictions made by TFTs via `dash`

### File Structure
- Submission.ipynb : Submission notebook for project submission to Udacity. Outlines the training process and provides a discussion of the data used in training
- dash_components/ : Contains the source files defining the application's layout and callback functionality
- models/ : Contains the model checkpoint files to be loaded at application startup
- data/ : Contains the training data files to be loaded at application startup
- cache/ : Local file cache used by application
- assets/ : Contains CSS style definitions.
- run_config.yml : Contains hyperparameters for model training and data preparation for prediction.
- covid_dashboard.py : Entry point for application

## Installation
Currently, the application is available only as a pure python script. To get the repository, either download it as an archive using GitHub's UI or clone it using the git Client of your choice or running:

```
git clone https://github.com/b-kaindl/COVID-19-Dashboard.git
```

### Installing Dependencies
Dependencies are defined in `requirements.txt` via flexible pinning. Running `update-deps.sh` updates the requirements in `requirements.lock` as fixed pins on the latest version number found using `pip`.

Optionally, you can create a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)
to install the required dependencies in an isolated way.

To use install the most recent version of each dependency, run

```
pip install -r requirements.txt
```

If you want to install the most recently locked version for each package, run:

```
pip install -r requirements.lock
```

## Usage
### Preparing Model and Data for Usage
**NOTE: This repository comes with a pre-trained model and a dataset with the necessary configuration.**
**If you just want to explore the application, you can skip ahead to the next section!**

To use a model with the application, put its `.ckpt` file into `/models` and the dataset used during training into `/data`. make sure that, the model file needs the file ending `.ckpt` so that the model loader can pick it up and display it in the dropdown.

Finally, make sure that the `run_config.yml` file in the project root is the same as the one used during model training. Optionally you can modify the hyperparameters to match those used during model training.


### Running the application
To spin up the dashboard navigate to the project root folder and run

```
python3 covid_dashboard.py
```

The prompt will give you a URL you can navigate to to view the app. As the application will download the most recent dataset from OWID, the startup might take a little while.

Upon navigating to the prompted URL, you can choose a model in the "Prediction Model" dropdown. Make sure to choose a model that matches the parameters defined in `run_config.yml`. Select the matching training data set and wait for the app to finish loading. Finally, you can select among the available countries in the country dropdown list to have the predictions for the corresponding country displayed together with the prediction quantiles.



## Contributing
As this project is licensed under the conditions of the [MIT Licensing Aggreement](https://github.com/b-kaindl/COVID-19-Dashboard/blob/main/LICENSE) you are free (and welcome!) to fork this project or contribute to it via PR. For pragmatic reasons I could only train a simple model for demonstration purposes.

If you want to train your own model, I suggest you havee a look at the submission notebook included in this repository, which outlines the training process I followed. The code sections that are commented out should give an idea on how to implement a training pipeline for your own model.

Should you decide to use `wandb` for organizing the experimentation process, you can [Contact Me](mailto:bernhard.kaindl.suppan@gmail.com) to get permissions to submit model and data artifacts to [the existing workspace](https://wandb.ai/kaiharuto/capstone) for this project. Should you use your own project, I would still be glad to know!
