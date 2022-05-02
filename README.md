# TelemannGenerator

Program to realize the inner voices programmatically of Telemann (and other baroque styled) chorales. Part of The Telemann Chorale Project: A Computational Study of Creativity in Baroque Vocal Music

## Linux Installation

1. First, install Magenta's dependencies:

```bash
sudo apt-get install libjack-dev
sudo apt-get install libasound2-dev
```

2. Next, run the installation script, which assumes you have python3.8 installed on your machine:

```bash
chmod +x bin/install.sh
./bin/install.sh
```

3. Activate and deactivate your virtual environment with:

```bash
source env/bin/activate   # Activate
deactivate                # Deactivate
```

Optionally, add the following alias to your `~/.bash_aliases` file to activate a virtual environment with `act` instead of the above command:

```bash
# In ~/.bash_aliases
alias act='source env/bin/activate'

# Run source ~/.bash_aliases to update your shell
```

## Git Tutorial

### Git Basics

#### Overview

Git is a distributed version control system. This means that it is used for keeping track of multiple versions of the source code across multiple machines. This is powerful for two main reasons: 1. it allows developers to work independently, and 2. it ensures that changes that are synchronized with a remote server are not lost in case your local copy is destroyed.

Here is a useful visualization of Git and what to do if you get lost: https://ndpsoftware.com/git-cheatsheet.html#loc=index;.

### Tracking, Commits, Remote

To keep track of changes to a file, you have to explicitly tell Git to track them for you. You do this via the `git add {file name}` command, which tells Git to include it in your next commit:

```bash
# Say you made some important file you want to keep track of in your project
touch hello.txt

# If you run `git status`, it will be listed under "Changes not staged for commit"
# To start tracking it and include it in your next commit, run git add on it:
git add hello.txt

# Now if you run `git status`, it will be listed under "Changes to be committed"
```

A commit is a snapshot of the entire source code at the moment you type `git commit`, including any changes you told Git to include with `git add`.

```bash
# Typing `git commit` brings up an editor to type a commit message.
# This is often more annoying than useful, so passing in the `-m` flag
# allows you to pass in a commit message with the command directly.
git commit -m "Adding hello.txt"
```

You can see the history of your Git repository with `git log`. This will also show you which commits other branches are synchronized with.

To ensure that your code will not be lost in case your local machine fails, it's necessary to synchronize it with a remote repository. For this project, we are using GitHub, although you may have used something like GitLab in the past. GitHub is simply a service that provides servers to store copies of your code so that other developers can pull it, make changes to it, and update it. It is important to understand that GitHub != Git: Git is a program to manage version control tracking, GitHub is a platform that stores versions of the code remotely.

```bash
# To synchronize with GitHub, just type `git push`
git push
```

### Branches

For the purposes of our project, everyone is going to have their own separate branch in the Git version control system. A branch is a copy of the source code of a project at the moment it is created, and allows you to work independently of other developers on the team. Whenever you are working on a new feature, do it in your own branch. When that feature is completed, you will want to update the `main` branch with those changes, and then update your own branch with the `main` branch as well. To do so, you will want to create a pull request on GitHub: https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request#creating-a-pull-request. This will allow other developers to peruse your code and make sure there aren't any issues.

Creating a new branch:

```bash
# First, make sure you are on the main branch:
git status  # Should say "On branch main"

# To create a branch, run
git checkout -b {new branch name}
# Such as
git checkout -b dev-alex

# To see all branches, both local and remote, run
git branch -a

# To switch between branches, use the git checkout command:
git checkout main      # Switches to main
git checkout dev-alex  # Switches to dev-alex if it exists locally\
```

Making a change in a personal branch:

```bash
# Common pattern for making changes on a personal branch:
git checkout dev-alex
touch hello.txt
git add hello.txt
git commit -m "Adding hello.txt"
git push
# If Git fails and says something like:
#   fatal: The current branch dev-alex has no upstream branch.
# This means that you have never pushed this branch to the remote servers on GitHub.
# Run the command it tells you to do so so that Git knows where on GitHub to push to
git push --set-upstream origin dev-alex
```

Synchronizing with main:

```bash
# Now that changes are pushed, read through this article to create a pull request (PR) on GitHub
# https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request#creating-a-pull-request

# Once the PR is accepted and merged into main, you will want to update your own branch with the changes on main
# We can do this by using `git rebase`, which avoids the ugly "Merge branch ... from ... into ..." commit message from simple merging
git checkout main
git pull  # Get the changes from the accepted PR
git checkout dev-alex
git rebase main

# Rebasing may result in some conflicts, though usually it is painless
# If merge conflicts appear, just follow the instructions on screen
# Afterwards, you want to synchronize GitHub with your updated local branch:
git push
```
