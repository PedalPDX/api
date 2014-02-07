PedalAPI
========

Current Version = 0.3
---------------------

Depends
-------
* Flask
* Markdown

Commands
--------

| Type   | Command                                       | Result                                                |
| :----- | :-------------------------------------------- | :---------------------------------------------------- |
| GET    | server.address.com:5000/                      | Returns this README                                   |
| GET    | server.address.com:5000/version               | Returns the current version of the PedalAPI           |
| GET    | server.address.com:5000/pedal/0.3/rides       | Returns all know ride ID's                            |
| GET    | server.address.com:5000/pedal/0.3/rides/{ID}  | Returns information on the specified id               |
| GET    | server.address.com:5000/pedal/0.3/rides/new   | Returns a random ID to be used to upload a new ride   |
| POST   | server.address.com:5000/pedal/0.3/rides       | Used for uploading ride information including ID      |
| POST   | server.address.com:5000/pedal/0.3/rides/{ID}  | Used for uploading ride information to a specific ID  |
