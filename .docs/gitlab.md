# GitLab

### Workflow
* After creating a project, you need to run the generated code through the formatter and commit the code to the main branch
* Subsequent MRs should not contain source template files, this complicates the code review process

### Authorization
* Get a personal token in GitLab, without 'Expiration date' and with `read_api` and `read_registry` rights
1. Click on your avatar in the upper right corner and go to the Preferences menu.
2. From the sidebar, go to Access Tokens.
3. Create a new personal token:
1. In the Token name field, enter the purpose of the token.
2. Leave the Expiration date field empty.
3. Select the `read_api`, `read_registry` permission set.
4. Click Create personal access token. Copy the token and save it in a safe place.
* Add a token to .profile `export DOCKER_GITLAB_TOKEN=<TOKEN>` and user `export DOCKER_GITLAB_USER=<USER>@tripster.ru`, replacing `<USER>` and `<TOKEN>` with your own
* Or add these variables to .env-taskfile
* execute `source ~/.profile` to pull changes, you can check via `echo "user=$DOCKER_GITLAB_USER : token=$DOCKER_GITLAB_TOKEN"`
* Execute `task docker:login:gitlab` to login to GitLab Container Registry
