#!/bin/bash

# Define the emails
OLD_EMAIL="tn7956666@gail.com"
CORRECT_NAME="Duong"
CORRECT_EMAIL="tn7956666@gmail.com"

# Refresh index cache to prevent phantom "unstaged changes" on Windows
git update-index -q --refresh

# Stash any real unstaged/staged changes so filter-branch can proceed
STASH_RESULT=$(git stash --include-untracked 2>&1)
STASHED=0
if echo "$STASH_RESULT" | grep -q "Saved working directory"; then
  echo "Stashed local changes temporarily."
  STASHED=1
fi

echo "Rewriting history to change $OLD_EMAIL to $CORRECT_EMAIL..."

# Run git filter-branch with -f to overwrite backup refs
git filter-branch -f --env-filter '
if [ "$GIT_COMMITTER_EMAIL" = "tn7956666@gail.com" ]
then
    export GIT_COMMITTER_NAME="Duong"
    export GIT_COMMITTER_EMAIL="tn7956666@gmail.com"
fi
if [ "$GIT_AUTHOR_EMAIL" = "tn7956666@gail.com" ]
then
    export GIT_AUTHOR_NAME="Duong"
    export GIT_AUTHOR_EMAIL="tn7956666@gmail.com"
fi
' --tag-name-filter cat -- --branches --tags

# Restore stashed changes if we stashed anything
if [ "$STASHED" -eq 1 ]; then
  git stash pop
  echo "Restored your local changes."
fi

echo "Done! If the output looks correct, run: git push --force"

# Copy the fix_git_email.sh file into the folder of the broken repository.
# Open a terminal inside that folder.
# Run the script using Bash:
# bash
# bash fix_git_email.sh
# If it completes successfully, update GitHub by running:
# bash
# git push --force
