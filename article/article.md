Hello everyone, I am a Data Platform or DataOps Engineer at [FreshBooks](https://www.freshbooks.com/). In this article I would like to share my experience on configure best practices in CI/CD pipelines. We had a linter configuration that developers could run before submitting PR. We understand that we want to integrate that checks into our regular CI/CD pipeline. This adoption helps to eliminate potential errors, bugs, stylistic errors, and basically have the common code style across the team.  

We are in FreshBooks using GitHub as a home for our code base, so we would like to use it as much as possible. Recently I finished this configuration so linter and its checks are now part of GitHub actions CI/CD workflow.

This article has two major parts: the first one is linter configuration, and the second one is GitHub workflow configuration itself. Feel free to read all the parts, or skip some and jump into specific one you are interested in.

- [Linters configuration](#linters-configuration)
  * [Disable unwanted checks](#disable-unwanted-checks)
    + [Documentation](#documentation)
    + [Import error](#import-error)
    + [Tweaks for airflow code](#tweaks-for-airflow-code)
- [GitHub workflow actions CI/CD configurations](#github-workflow-actions-ci-cd-configurations)
  * [When to run it](#when-to-run-it)
  * [What files does it run against to](#what-files-does-it-run-against-to)
  * [Run linter itself](#run-linter-itself)
- [Conclusion](#conclusion)

## Linters configuration

Here are the linters and checks we are going to use:

- [flake8](https://flake8.pycqa.org/en/latest/)
- [flakeheaven](https://flakeheaven.readthedocs.io/en/latest/)
- [black](https://github.com/psf/black)
- [isort](https://github.com/PyCQA/isort)

**Disclaimer**: author assumes you are familiar with the above-mentioned linters, tools, and checks.

I would like to share how to configure it for the python project. I prepared a full [github actions python configuration demo repository](https://github.com/iamtodor/github-actions-python-demo).

We use `flakeheaven` as a `flake8` wrapper, which is very easy to configure in one single `pyproject.toml`. The whole `pyproject.toml` configuration file could be found in
a [demo repo](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/pyproject.toml).
~
![pyproject.toml](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-pyproject-config.png?raw=true)

I would say the config file is self-explainable, so I will not stop here for a while. Just a few notes about tiny tweaks.

### Disable unwanted checks

A few checks that we don't want to see complain about:

#### Documentation

Default `flakeheaven` configuration assumes every component is documented.

```
>>> python -m flakeheaven lint utils.py

utils.py
     1:   1 C0114 Missing module docstring (missing-module-docstring) [pylint]
  def custom_sum(first: int, second: int) -> int:
  ^
     1:   1 C0116 Missing function or method docstring (missing-function-docstring) [pylint]
  def custom_sum(first: int, second: int) -> int:
  ^
     5:   1 C0116 Missing function or method docstring (missing-function-docstring) [pylint]
  def custom_multiplication(first: int, second: int) -> int:
```

We are ok if not every module will be documented. We are ok if not every function or method will be documented. We are not going to push documentation for documentation's sake. So we want to disable `C0114` and `C0116` checks from pylint.

![flakeheaven disable docs](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-disable-docs.png?raw=true)

#### Import error

Our linter requirements live in a separate file, and we don't aim to mix it with our main production requirements. Hence, linter would complain about import libraries as linter env does not have production libraries, quite obvious.

```
>>> python -m flakeheaven lint . 

dags/dummy.py
     3:   1 E0401 Unable to import 'airflow' (import-error) [pylint]
  from airflow import DAG
  ^
     4:   1 E0401 Unable to import 'airflow.operators.dummy_operator' (import-error) [pylint]
  from airflow.operators.dummy_operator import DummyOperator
  ^
```

So we need to disable `E0401` check from `pylint`.

Also, there is another possible solution to disable this check is to include `# noqa: E0401` into the import statement. 

```python
from airflow import DAG  # noqa: E0401
from airflow.operators.dummy_operator import DummyOperator  # noqa: E0401
```

![flakeheaven disable import checks](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-disable-import-checks.png?raw=true)

We assume that the developer who writes the code and imports the libs is responsible for the writing reliable tests. So if the test does not pass it means that it's something with import or a code (logic) itself. Import check is not something we would like to put as a linter job.

#### Tweaks for airflow code

To configure code for Airflow DAGs there are also a few tweaks. Here is the dummy example `dummy.py`.

![python dummy DAG](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/python-airflow-tasks-order.png?raw=true)

If we run `flakeheaven` with the default configuration we would see the following error:

```
>>> python -m flakeheaven lint .                                                       

dags/dummy.py
    17:   9 W503 line break before binary operator [pycodestyle]
  >> dummy_operator_2
  ^
    18:   9 W503 line break before binary operator [pycodestyle]
  >> dummy_operator_3
  ^
    19:   9 W503 line break before binary operator [pycodestyle]
  >> [dummy_operator_4, dummy_operator_5, dummy_operator_6, dummy_operator_7]
  ^
```

However, we want to keep each task specified in a new line, hence we need to disable `W503` from pycodestyle.

![disable W503](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-diable-line-break-W503.png?raw=true)

Next, with the default configuration we would get the next warning:

```
>>> python -m flakeheaven lint .                                                       

dags/dummy.py
    15:   5 W0104 Statement seems to have no effect (pointless-statement) [pylint]
  (
  ^
```

This is about how we specify task order. The workaround here is to exclude `W0104` from pylint.

![disable W0104](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-disable-statement-no-effect-W0104.png?raw=true)

More info about rules could be found on [flake8 rules page](https://www.flake8rules.com/). 

## GitHub workflow actions CI/CD configurations

**Disclaimer**: author assumes you are familiar with [GitHub actions](https://github.com/features/actions).

We configure GitHub Workflow to be triggered on every PR against the main (master) branch.

The whole `py_linter.yml` config could be found in a [demo repo](https://github.com/iamtodor/github-actions-python-demo/blob/main/.github/workflows/py_linter.yml). I will walk you thru it step by step.

![py_linter.yml](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-full.png?raw=true)

### When to run it

We are interested in running linter only when PR has `.py` files. For instance, when we update `README.md` there is no sense to run python linter.

![configure run workflow on PRs and push](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-py-push-pr.png?raw=true)

### What files does it run against to

We are interested in running a linter only against the modified files. Let's say, we take a look at the provided repo, if I update `dags/dummy.py` I don't want to waste a time and resources running linter against `main.py`. For this purpose we use [Paths Filter GitHub Action](https://github.com/dorny/paths-filter), which is very flexible.

![Paths Filter GitHub Action](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-paths-filter.png?raw=true)

If we have in one PR modified `.py` and any other files such as `.toml`, we don't want to run linter against not `.py`, so we use where we configured filtering only for `.py` files no matter its location: root, tests, src, etc.

The changed file can have the following statuses `added`, `modified`, or `deleted`. There is no reason to run a linter against deleted files as your workflow would simply fail, because there is no more that particular changed file in the repo. So we need to configure what changes we consider to trigger linter.

![added|modified](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-added-modified.png?raw=true)

I define the variable where I can find the output (the only `.py` files) from the previous filter. This variable would contain modified `.py` files, that I can further pass to a `flakeheaven`, `black`, and `isort`. By default, the output is disabled, and Paths Changes Filter allows you to customize it: you can list the files in `.csv`, `.json`, or in a `shell` mode. Linters accept files separated simply by space, so our choice here is `shell` mode.

![list files shell](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-list-files-shell.png?raw=true)

### Run linter itself

The next and last step is to run the linter itself.

![run linter step](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-run-linter-step.png?raw=true)

Before we run linter on changed files we run a check if there is an actual change in `.py` files, if there are any `.py` files from the previous step.

![check if there are .py files](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-run-linter-check-for-changes.png?raw=true)

Next, using the before-mentioned output variable we can safety pass the content from this `steps.filter.outputs.py_scripts_filter_files` variable to linter.

![linter commands](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-run-linter-commands.png?raw=true)

## Conclusion

That's all I would like to share. I hope it is useful for you, and that you can utilize this experience and knowledge. 

I wish you to see these success checks every time you push your code :)

![success linter](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/linter-success.png?raw=true)

If you have any questions feel free to ask in a comment section, I will do my best to provide a comprehensive answer for you. 

Question to you: do you have linter checks as a part of your CI/CD?

Todor1995!