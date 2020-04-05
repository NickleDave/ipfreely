![Moe from the Simpsons shouting "Hey! Everybody! I pee freely" to a bar full of people](./doc/images/ipfreely.gif)

ipfreely
========

ipfreely emails you when your dynamic IP address changes

Features
--------
- ip addresses
- emails

Installation
------------

1. `$ pip install ipfreely`
2. create a throwaway email account that you won't mind if it gets hacked
3. `$ python ipfreely --from throwaway_address throwaway_password`
4. `$ python ipfreely --to your_actual_email@gmail.probably.com`

Usage
-----
`ipfreely` runs through a command-line interface.

For a list of commands you can run
```console
$ ipfreely -h
``` 

Currently it only works with gmail; you'll want to set up a throwaway account and 
in the account settings turn [Allow less secure apps to ON](https://myaccount.google.com/lesssecureapps).



Contribute
----------

- Issue Tracker: https://github.com/NickleDave/ipfreely/issues

Change Log
----------
[is here](doc/CHANGELOG.md)

License
-------
[BSD](./LICENSE)
