Hi, Solver! Welcome to the

# MLflow tutorial

To run the example have Miniconda or Anaconda installed and set an environment variable(on Linux) like so:

```bash
export MLFLOW_CONDA_HOME=/home/foo/miniconda3
```
You might want to move previous line to .bashrc(on Linux).
For Windows just use the environment variables.
Then

```bash
pip install mlflow
```

Then run the example:

```bash
mlflow run . -P k_low=3 k_high=5
```

or with default params


```bash
mlflow run .
```
Note: It will take some time to install the virtual environment.

You can then check your mlflow runs:
```bash
mlflow ui
```

Keep on learning and things solving!
