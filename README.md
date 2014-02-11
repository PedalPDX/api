PedalAPI
========

Depends
-------
* Flask
* Markdown

Commands
--------

| Type | Command                            | Result                                      |
| :----| :----------------------------------| :------------------------------------------ |
| GET  | server.address.com:5000/           | Returns this README                         |
| GET  | server.address.com:5000/version    | Returns the current version of the PedalAPI |
| GET  | server.address.com:5000/rides      | Returns all know ride ID's                  |
| GET  | server.address.com:5000/rides/{ID} | Returns information on the specified id     |
| POST | server.address.com:5000/rides      | Used for uploading ride information         |
