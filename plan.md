

# Using the environment: 
## To set up your environment (Do this if its the first time you work on the project or when the requirements.txt file changes):

1. Open terminal in the top level of the repo (at root, where README.md is)
2. run `virtualenv venv --python=python3`
3. run `source venv/bin/activate`
4. run `pip install -r requirements.txt` 
5. You shouldn't have received any errors after installing the requirements. You should be good to go. Make sure you don't commit your personal virtual environment to github

## Every time you develop

1. Activate the virtual environment
2. run `python manage.py migrate` from the same location as manage.py


---
# Meetings

Probably use Django
Front end/UI probably least important, can be saved till later
How can we split the work up?
Enforce HTTP Basic Auth
Restfl API
Friend reqeusts

Workflow:
Ensure each of us has our own working branch
Only merge with master when we know it wont fudge anything up
we should probably make some unit tests for our program tbh

first steps:
probably make our website template
this way we can each work on different sections independent from one another
make upload, submission pages, or would these be popouts with javascript?
trello board to manage work section, who's working on what
design mockups will need to be made at one point, not for marks but for our own sanity

Feb 22:
Made Heroku,
Going to do vue front end,
Can split up tasks and each person does front end and back end for their tasks?
We should make mockups - we'll take some topics each and make mockups for them
Ben making mockups, app should be deployed in heroku

