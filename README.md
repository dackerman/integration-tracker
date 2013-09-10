Release branch Integration Tracker
==================================

Introduction
------------
This is a messy little python program that lets you keep track of your integration branches in git.  As an example, say you have a release branch called `1.0-release` and `master` (which is the next release in development).  You probably only want to check in bug fixes into your release branch, but you always want to make sure that most commits you do on the release branch are also cherry-picked onto master to prevent regressions.  It's easy to forget to do this, so this tool will analyze both your branches and find commits that you probably want to look at.

Usage
-----
Create a file called `integrations.txt` somewhere in your git directory, and create one line per integration.  Below is an example file where you have two versioned release branches, 1.0-release and 2.0-release, and the active master branch. You want to make sure 1.0 fixes go into 2.0 and master, and you want to make sure 2.0 fixes make it into master.

    1.0-release -> 2.0-release
    1.0-release -> master
    2.0-release -> master

This tells the program that you have three integrations to keep track of.

Next, run the program in the same directory as the file with `python integration-tracker.py`.  You'll see something like this:

    1.0-release -> 2.0-release: Found 1 fishy commit you should look at.
    1.0-release -> master: Found 1 fishy commit you should look at.
    2.0-release -> master: Found 0 fishy commits you should look at.

This means you either forgot to integrate a commit from 1.0 into both 2.0 and master, or potentially made an equivalent commit, but didn't reference the original commit in the body of the message.  Either way, it needs to be verified by a human.

If you open up `integrations.txt` now, you'll see the program has updated the file with your fishy commits:

    1.0-release -> 2.0-release
    ? some.user@gmail.com 1378779384 7fa3ad8c8959d0553f4365b7fa936c85c1882031 fixed horrible bug
    1.0-release -> master
    ? some.user@gmail.com 1378779384 7fa3ad8c8959d0553f4365b7fa936c85c1882031 fixed horrible bug
    2.0-release -> master

And, there are your commits!  You have all the information you need to check out the commit and make sure it's properly integrated.  Now, if you forgot to do the cherry-pick, then when you do this, it will remove the entry from the file the next time you run the command, assuming you didn't have to resolve any conflicts or used the `-x` option on `cherry-pick` to include the original hash from the integration.

If you had to manually integrate the changes, then this tool may not be able to determine the fact that it has been integrated. If this is the case, then simply change the `?` at the beginning of the line to something else (maybe 'm' for 'manual') to let the program know that you've handled it and it shouldn't bother you about that commit again.