1- Create a virtual environment for the project (Inside the project folder)

    python3 -m venv myenv
    cd myenv/Scripts/
    activate

2- Navigate to the project directory and install the dependencies from the requirements.txt file:

    pip install -r requirements.txt

This will install all the required packages with their specific versions mentioned in the requirements.txt file.

3 - Setup Mysql Database:

    - Create a database and add the credentials to "DB_config.py" file

4 - Start the Flask application:

    flask run

This should start the Flask application on your local machine.
If any new dependencies are added to the requirements.txt file, you'll need to repeat step 2 to install them.
