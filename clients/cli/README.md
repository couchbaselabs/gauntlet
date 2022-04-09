## E2E Cli
Interface to test available microservice endpoint from user level

#### Install Requirements
``pip3 install -r requirements.txt``

#### Script Usage

```
$ python3 e2e.py --help 
Usage: e2e.py [OPTIONS] COMMAND [ARGS]...

Options:
  -u, --username TEXT  Username
  -p, --password TEXT  Password
  --config TEXT        Config for the interface
  --help               Show this message and exit.

Commands:
  flight
  profile
```

#### Sample outputs

###### Create new user profile
```
$ python3 e2e.py profile create-user --username testuser --password asdasd -f Fname -l Lname
Creating user 'testuser'
User Created Successfully
```

###### Book flight ticket
```
$ python3 e2e.py -u testuser -p asdasd profile book-flight --flight_id AA001_08162021 --num_seats 1 --wallet 123456
```
