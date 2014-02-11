PedalAPI
========

Current Version = 0.4
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
| POST   | server.address.com:5000/pedal/0.3/rides       | Used for uploading ride information                   |
