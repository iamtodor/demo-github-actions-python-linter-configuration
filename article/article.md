Linter helps and advises us about code quality by running sanity checks and displaying warnings and errors about code
smells. Also, potentially it helps to prevent bugs in a project.

As we are in FreshBooks using GitHub, so we would like to use it as much as possible.

Recently I was involved in configuring linters as a part of CI/CD in GitHub actions.

## Linters configuration

I would like to share how to configure it for the python project. I prepared a full [github actions python configuration demo repository](https://github.com/iamtodor/github-actions-python-demo).

We use flakeheaven as a flake8 wrapper, which is very easy to configure in one single `pyproject.toml` configuration file.
The whole `pyproject.toml` configuration file could be found in
a [repo](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/pyproject.toml).

![pyproject.toml](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-pyproject-config.png?raw=true)

Disclaimer: author assumes you are familiar with the above-mentioned linters, tools, and checks. I would say the config file
is self-explainable, so I will not stop here for a while. Just a few notes about tiny tweaks.

A few checks that we don't want to see complain about:

### Documentation

We are ok if not every module will be documented. We are ok if not every function or method will be documented.

![flakeheaven disable docs](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-disable-docs.png?raw=true)

### Import issues

Our linter requirements live in a separate file, and we don't aim to mix it with our main production requirements.
Hence, linter could complain about import libraries as linter env does not have production libraries, quite obvious. So
we need to disable this check. We assume that the developer who writes the code and imports the libs is responsible for
the tests. So if the test does not pass it means that it's something with import or a code itself. Import checks it's
not something we would like to put as a linter job.

![flakeheaven disable import checks](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-disable-import-checks.png?raw=true)

### Tweaks for airflow code

To configure code for Airflow DAGs there are also a few tweaks. Here is the dummy example `dummy.py`.

![python dummy DAG](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/python-airflow-tasks-order.png?raw=true)

If we run flakeheaven with the default configuration we would see the following error:

```
 python -m flakeheaven lint .                                                       

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

However, we want to keep each task specified in a new line, hence we need to disable `W503` from pycodestyle: Disable
line break before binary operator.

![disable W503](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-diable-line-break-W503.png?raw=true)

Next, with the default configuration we would get the next warning:

```
python -m flakeheaven lint .                                                       

dags/dummy.py
    15:   5 W0104 Statement seems to have no effect (pointless-statement) [pylint]
  (
  ^
```

The workaround here is to exclude `W0104` from pylint: Statement seems to have no effect (pointless-statement). This is about how we
specify task order.

![disable W0104](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/flakeheaven-disable-statement-no-effect-W0104.png?raw=true)

## GitHub actions configurations

**Disclaimer**: author assumes you are familiar with [GitHub actions](https://github.com/features/actions).

We configure GitHub Workflow to be triggered on every PR against the main (master) branch.

Here are the linters and checks we are going to use:

- [flake8](https://flake8.pycqa.org/en/latest/)
- [flakeheaven](https://flakeheaven.readthedocs.io/en/latest/)
- [black](https://github.com/psf/black)
- [isort](https://github.com/PyCQA/isort)

The whole `py_linter.yml` config could be found in
a [repo](https://github.com/iamtodor/github-actions-python-demo/blob/main/.github/workflows/py_linter.yml). I will walk you thru it step by step.

![py_linter.yml](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-full.png?raw=true)

We are interested in running linter only when PR has `.py` files. For instance, when we update `README.md` there is no sense to run python linter.

![configure run workflow on PRs and push](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-py-push-pr.png?raw=true)

We are interested in running a linter only against the modified files. Let's say, we take a look at the provided repo, if I update `dags/dummy.py` I don't want to waste a time and resources running linter against `main.py`. For this purpose we use [Paths Filter GitHub Action](https://github.com/dorny/paths-filter), which is very flexible.

![Paths Filter GitHub Action](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-paths-filter.png?raw=true)

If we have in one PR modified `.py` and any other files such as `.toml`, we don't want to run linter against not `.py`, so we use where we configured filtering only for `.py` files no matter its location: root, tests, src, etc.

The changed file can have the following statuses `added`, `modified`, or `deleted`. There is no reason to run a linter against deleted files as your workflow would simply fail, because there is no more that particular changed file in the repo. So we need to configure what changes we consider to trigger linter.

![added|modified](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-added-modified.png?raw=true)

I define the variable where I can find the output (the only `.py` files) from the previous filter. This variable would contain modified `.py` files, that I can further pass to a `flakeheaven`, `black`, and `isort`. By default, the output is disabled, and Paths Changes Filter allows you to customize it: you can list the files in `.csv`, `.json`, or in a `shell` mode. Linters accept files separated simply by space, so our choice here is `shell` mode.

![list files shell](https://github.com/iamtodor/github-actions-python-configuration-demo/blob/main/article/img/gh-config-list-files-shell.png?raw=true)

### Run linter

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
