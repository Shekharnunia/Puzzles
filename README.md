# Puzzles
A University oriented social network to make a better Community

## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/Shekharnunia/Puzzles.git
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Create the database:

```bash
python manage.py migrate
```

Finally, run the development server:

```bash
python manage.py runserver
```

The project will be available at **127.0.0.1:8000**.
