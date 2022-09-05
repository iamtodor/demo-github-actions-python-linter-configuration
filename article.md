Linter helps and advises us about code quality by running sanity checks and displaying warnings and errors about code smells. Also, potentially it helps to prevent bugs in a project.

As we are in FreshBooks using GitHub, so we would like to use it as much as possible.

Recently I was involved in configuring linters as a part of CI/CD in GitHub actions.

## Linters configuration

I would like to share how to configure it for the python project. I prepared a full [
github actions python configuration demo repository](https://github.com/iamtodor/github-actions-python-demo).

We use flakeheaven as flake8 wrapper, which is very easy to configure in one single `pyproject.toml` configuration file. The whole `pyproject.toml` configuration file could be found in a [repo](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/pyproject.toml).

![pyproject.toml](https://i.imgur.com/nNDptBv.png)

Disclaimer: author assumes you are familiar with above-mentioned linters, tools, and checks. I would say the config file is self-explainable, so I will not stop here for a while. Just a few notes about tiny tweaks.

A few checks that we don't want to see complain about:

### Documentation

We are ok if not every module will be documented. We are ok if not every function or method will be documented.

![flakeheaven disable docs](https://i.imgur.com/pVfPuJJ.png)

### Import issues

Our linter requirements live in a separate file, and we don't aim to mix it with our main production requirements. Hence, linter could complain about import libraries as linter env does not have production libraries, quite obvious. So we need to disable this check. We assume that the developer who writes the code and imports the libs is responsible for the tests. So if the test does not pass it means that it's something with import or a code itself. Import checks it's not something we would like to put as a linter job.

![flakeheaven disable import checks](https://i.imgur.com/mYVC7fj.png)

### Airflow

In order to configure code for Airflow DAGs there are also a few tweaks. Here is the dummy example `dummy.py`.

## TODO
![flakeheaven disable import checks](https://i.imgur.com/mYVC7fj.png)

Firstly, we need to exclude `W0104` from pylint: Statement seems to have no effect (pointless-statement). This is about how we specify task order.

## TODO
![flakeheaven disable import checks](https://i.imgur.com/mYVC7fj.png)

Then we want to have each task be specified in a new line, hence we need to disable `W503` from pycodestyle: Disable line break before binary operator.

## TODO
![flakeheaven disable import checks](https://i.imgur.com/mYVC7fj.png)

## GitHub actions configurations

Disclaimer: author assumes you are familiar with [GitHub actions](https://github.com/features/actions)

We configure GitHub Workflow to be triggered on every PR against main (master) branch.

Here are the linters and checks we are going to use:

- [flake8](https://flake8.pycqa.org/en/latest/)
- [flakeheaven](https://flakeheaven.readthedocs.io/en/latest/)
- [black](https://github.com/psf/black)
- [isort](https://github.com/PyCQA/isort)

The whole `py_linter.yml` config could be found in a [repo](https://github.com/iamtodor/github-actions-python-demo/blob/main/.github/workflows/py_linter.yml). We will walk thru it step by step.

![py_linter.yml](https://i.imgur.com/UkErWeG.png)

We are interested in running linter only when PR has `.py` files. For instance, when we update `README.md` there is no sense to run python linter.

![configure run workflow on PRs and push](https://i.imgur.com/4B5JLqi.png)

We are interested in running a linter only against the modified files. Let's say, we take a look at the provided repo, if I update `dags/dummy.py` I don't want to waste a time and resources running linter against `main.py`. For this purpose we use [Paths Filter GitHub Action](https://github.com/dorny/paths-filter), that is very flexible.

If we have in one PR modified `.py` and `.toml` files, we don't want to run linter against `.toml`, so we use  where we configured filtering only for `.py` files no matter its location: root, tests, src, etc.

![Paths Filter GitHub Action](https://i.imgur.com/B9lu9ki.png)

As a changed file can be `added`, `modified`, or `deleted`, there is no reason to run a linter against deleted file as your workflow would simply fail as there is no more than that particular changed file. So we need to configure what changes we consider to trigger linter.

![added|modified](https://i.imgur.com/YBrd8Ee.png)

I define the variable where I can find the output (the only `.py` files) from the previous filter. This variable would contain modified `.py` files, that I can further pass to a `flakeheaven`, `black`, and `isort`. By default, the output is disabled, and Paths Changes Filter allows to customize it: you can list the files in `.csv`, `.json` or in a `shell` mode. Linters accept files separated simply by space, so our choise here is `shell` mode.

![list files shell](https://i.imgur.com/0HjT6Wg.png)
