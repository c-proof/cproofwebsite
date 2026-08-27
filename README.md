# Page for C-PROOF website

Based off https://projectpages.github.io.


## Installing and editing.

The workflow is a typical `git` workflow.  You will need to install git.

1. Fork the repository to your own repositories by clicking the `Fork` button
on the upper-right in Github

2. Clone the repository to your machine: `git clone https://github.com/yourusername/website.git`

3. Make the `c-proof` version of the webpage a `remote` called `upstream`
`git remote add upstream https://github.com/c-proof/website.git`  We do this
so we can sync with other people's changes as they are merged on the original.

4. Checkout a new branch:  `git checkout -b new-branch-name`

4.  Edit something;  If you add new files remember to do `git add newfilepath/newfilename`.

5. Commit changes: `git commit -a -m "EDIT: helpful message about your change"`

6. Push the changes to *your* remote:   `git push origin new-branch-name`

7. Git will now suggest that you can make a pull request to `c-proof`.  Do so and then it will get merged if all is OK

8. The change will be automatically deployed to the website using a github action.

## Socials:

These are a constant struggle to keep straight with any sort of automated relay.
