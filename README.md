# Setup 

## Install Python 3.x with ```Miniconda```

Go [here](https://docs.conda.io/en/latest/miniconda.html##:~:text=Miniconda%20is%20a%20free%20minimal,zlib%20and%20a%20few%20others.) to install Miniconda.

Use the code below to confirm the ```checksum``` of the file.

```bash
echo -n "foobar" | openssl dgst -sha256
```

<br/>


## Install ```mysqlclient```

Run the code below to install ```mysqlclient```.

```bash
conda install mysqlclient
```

Make sure ```mysql-connector-python``` installs correctly.


## Install MySQL

Install MySQL with Homebrew. Check [this](https://gist.github.com/nrollr/3f57fc15ded7dddddcc4e82fe137b58e) gist to learn the installation process.


<br/>


# Creating your first data pipeline in Python

Access your local MySQL instance using the following command

```bash
mysql -u root -p
```

Create a new database called ```airflowdb``` using the following code.

```sql
CREATE DATABASE airflowdb CHARACTER SET utf8 COLLATE utf8_unicode_ci;
```

Create a new user for the database.

```sql
CREATE USER 'airflow'@'localhost' IDENTIFIED BY 'python2019'
```

Now we need to make sure the airflow user has access to the databases.

```sql
GRANT ALL PRIVILEGES ON *.* TO 'airflow'@'localhost';
FLUSH PRIVILEGES
```

Check the list of users to make sure the user was successfully added.

```mysql
SELECT user, host FROM mysql.user;
```

<img src='mysqlUsers.png' />


If you need to delete the user you just added, use the code below
```sql
DROP USER 'airflow'@'localhost'
```

<br/>

## Issues

### New Twitter API
Turns out you don't need the ```tweepy``` package to use Twitter's API. They recently released ```Twitter API v2``` which exposes several endpoints that can be used to manage tweets, get them, etc. You can find the documentation [here](https://developer.twitter.com/en/docs/twitter-api/data-dictionary/introduction).


### Date Format
Twitter uses the ISO-8901 spec for dates, thus, I had to use the ```dateutil``` library to parse the dates. You can find an interesting discussion between the core developers of CPython [here](https://discuss.python.org/t/parse-z-timezone-suffix-in-datetime/2220)


### MySQL config

[This](https://mathiasbynens.be/notes/mysql-utf8mb4#character-sets) article was very helpful to circumvent character-set issues associated with MySQL. In his article, Mathias explains why we should use the ```utf8mb4``` charset instead of the default ```utf8```. It turns out that MySQL partially implements ```utf-8```. Check out his blog to find out more, but here's the solution to dealing with unicode symbols in tweets and users' names.



```sql
# For each database:
ALTER DATABASE database_name CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
```

<br/>

Now change the charset for the ```tweet``` and ```user``` columns.

```sql
ALTER TABLE tbl_tweets CHANGE tweet tweet VARCHAR(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

ALTER TABLE tbl_tweets CHANGE user user VARCHAR(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

<br/>


Now we have to modify the config of MySQL which can be found at ```/usr/local/etc/my.cnf```. Modify the configuration according the code below:


```text
[client]
default-character-set = utf8mb4

[mysql]
default-character-set = utf8mb4

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

<br/>

Now run this code to confirm that the settings worked correctly.

```sql
SHOW VARIABLES WHERE Variable_name LIKE 'character\_set\_%' OR Variable_name LIKE 'collation%';
```

<br/>

## Prepare your database

<blockquote> Make sure you create a user with the right permissions </blockquote>

To observe the tasks their corresponding statuses, airflow uses a database. Thus it's essential that one is set up. Run ```airflow db init``` to initialise an ```SQLite``` database using ```alembic``` so that it matches the latest Airflow release.

```SQLite``` doesn't support parallelization. Thus, we'll use ```MySQL``` since we already have a MySQL DB setup.


<br/>

## Database backend settings for Celery

Go [here](https://docs.celeryq.dev/en/latest/userguide/configuration.html#database-backend-settings) to learn how to use a database backend.

```python
result_backend = 'db+scheme://user:password@host:port/dbname'
```


<br/>



## Authentication plugin ```caching_sha2_password``` cannot be loaded

You might run into this error with MySQL when you try to initialise your database in MySQL. Just configure it to run in ```mysql_native_password``` mode.

```sql
ALTER USER 'yourusername'@'localhost' IDENTIFIED WITH mysql_native_password BY 'youpassword';
```

 
<br/>


## Useful links to learn about ```Celery```.
- [First steps with Celery](https://docs.celeryq.dev/en/latest/getting-started/first-steps-with-celery.html#first-steps)
- [Database backend settings](https://docs.celeryq.dev/en/latest/getting-started/first-steps-with-celery.html#first-steps)


<br/>

## How to kill the airflow scheduler and the server

```bash
kill $(ps -o ppid= -p $(cat ~/airflow/airflow-webserver.pid))
```


## Dag definition

Checkout a sample pipeline definition [here](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html). Remember that ```sample_dag.py``` is just a dag definition file. The tasks defined in the script execute in a different context than the script self. Tasks are scheduled on different workers at different points in time; so this script cannot be used to communicate between tasks.

In the event that you want tasks to communicate with each other then you should explore a more advanced feature called [XComms](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html).


<br/>

### Default arguments

Tasks created as part of a ```DAG``` are simply instantiations of specific operators. These operators inherit from the ```BaseOperator```. For more information about the ```BaseOperator```'s parameters and what they do, refer to <code><b>airflow.models.BaseOperator</b></code> documentation.

<br/>

### Adding DAG and Tasks Documentation

DAG documentation supports only markdown at the moment, however task documentation supports:
- Plain text
- Markdown
- reStructuredText
- json
- yaml

<br/>

### Testing

A scheduler runs your task ***for*** a specific date and time, not ***at***.

```bash

# test print_date
airflow tasks test sample_dag_tutorial print_date 2022-05-05

# test sleep
airflow tasks test sample_dag_tutorial sleep 2022-05-05

# testing templated
airflow tasks test sample_dag_tutorial templated 2022-05-05

```

```airflow tasks test``` runs tasks locally, outputs their log to stdout, does not bother with dependencies, and does not communicate state (running, success, failed..) to the database. **It simply allows testing a single task instance.

The same applies to 

```bash
airflow dags test sample_dag_tutorial 2022-05-05
```




