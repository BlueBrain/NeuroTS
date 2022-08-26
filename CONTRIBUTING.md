# Contributing

We would love for you to contribute to this package and help make it even better than it is today!
As a contributor, here are the guidelines we would like you to follow:
* [Issues and Bugs](#issue)
* [Feature Requests](#feature)
* [Submission Guidelines](#submit)

## <a name="issue"></a> Got a question or found a bug?

If you have a question or find a bug in the source code, you can help us by
[submitting an issue](#submit-issue) to our [GitHub Repository][github]. Even better, you can
[submit a Pull Request](#submit-pr) with a fix.

## <a name="feature"></a> Missing a Feature?

You can *request* a new feature by [submitting an issue](#submit-issue) to our
[GitHub Repository][github]. If you would like to *implement* a new feature, please submit an
issue with a proposal for your work first, to be sure that we can use it. Then
[submit a Pull Request](#submit-pr) that points to this issue.

Please consider what kind of change it is:
* For a **Major Feature**, first open an issue and outline your proposal so that it can be
discussed. This will also allow us to better coordinate our efforts, prevent duplication of work,
and help you to craft the change so that it is successfully accepted into the project.
* **Small Features** can be crafted and directly [submitted as a Pull Request](#submit-pr).

## <a name="submit"></a> Submission Guidelines

### <a name="submit-issue"></a> Submitting an Issue

Before you submit an issue, please search the issue tracker, maybe an issue for your problem
already exists and the discussion might inform you of workarounds readily available.

We want to fix all the issues as soon as possible, but before fixing a bug we need to reproduce
and confirm it. In order to reproduce bugs we will need as much information as possible, a
[Minimal Working Example](https://stackoverflow.com/help/minimal-reproducible-example), and
preferably be in touch with you to gather information.

### <a name="submit-pr"></a> Submitting a Pull Request (PR)

When you wish to contribute to the code base, please consider the following guidelines:
* Make a [fork](https://guides.github.com/activities/forking/) of this repository.
* Make your changes in your fork, in a new git branch:

  ```shell
  git checkout -b my-fix-branch main
  ```

* Create your patch, **including appropriate test cases** (please note that the coverage must
  always be equal to 100%).
* Run the full test suite, and ensure that all tests pass (at least with one of the required
  python interpreters):

  ```shell
  tox
  ```

  or

  ```shell
  tox -e py38 -e lint -e docs -e check-packaging
  ```

* Commit your changes using a descriptive commit message.

  ```shell
  git commit -a
  ```

  Note: the optional commit `-a` command line option will automatically **add** and **rm** edited
  files.
* Push your branch to GitHub:

  ```shell
  git push --set-upstream origin my-fix-branch
  ```

* In GitHub, send a Pull Request to the `main` branch of the upstream repository of the relevant
  component.
* If we suggest changes then:
  * Make the required updates.
  * Re-run the test suites to ensure tests are still passing.
  * Rebase your branch and force push to your GitHub repository (this will update your Pull
    Request):

    ```shell
    git rebase main -i
    git push -f
    ```

That's it! Thank you for your contribution!

#### After your pull request is merged

After your pull request is merged, you can safely delete your branch and pull the changes from the
main (upstream) repository:
* Delete the remote branch on GitHub either through the GitHub web UI or your local shell as follows:

  ```shell
  git push origin --delete my-fix-branch
  ```

* Check out the main branch:

  ```shell
  git checkout main
  ```

* Delete the local branch:

  ```shell
  git branch -D my-fix-branch
  ```

* Update your main with the latest upstream version:

  ```shell
  git pull --ff upstream main
  ```

### <a name="release"></a> Releasing a new version

Releasing a new version can only be done by the maintainers.

The release process is the following:
* Checkout the main branch and ensure your local version is up to date:

  ```shell
  git checkout main
  git pull
  ```

* Create a new branch locally:

  ```shell
  git checkout -b release_X.Y.Z
  ```

* Update the CHANGELOG file using auto-changelog (see https://www.npmjs.com/package/auto-changelog):

  ```shell
  auto-changelog -v X.Y.Z
  ```

* Commit and push the new changelog:

  ```shell
  git commit -m "Release X.Y.Z"
  git push --set-upstream origin release_X.Y.Z
  ```

* Open a new pull request from this branch and merge it.
* Create a new release on GitHub.
* Checkout the main branch and update it:

  ```shell
  git checkout main
  git pull
  ```

* Remove your local branch:

  ```shell
  git branch -D release_X.Y.Z
  ```

After these steps the CI should automatically build the wheel and push it to pypi.

[github]: https://github.com/BlueBrain/NeuroTS
