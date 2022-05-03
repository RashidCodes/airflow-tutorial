# Setup (In Progress)

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
CREATE USER 'airflow'@'localhost' IDENTIFIED BY 'thisIsAwesome@20'
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


Now run this code to confirm that the settings worked correctly.

```sql
SHOW VARIABLES WHERE Variable_name LIKE 'character\_set\_%' OR Variable_name LIKE 'collation%';
```




