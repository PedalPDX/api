PedalAPI
========

Depends
-------
* Flask
* Markdown

About the API
-------------
This API is for use by the [PedalPDXApplication](http://pedal.cs.pdx.edu) bicycle route tracking application.

Commands
--------

| Type  | Command                             | Result                                        |
| :---- | :---------------------------------- | :------------------------------------------   |
| GET   | server.address.com:5000/            | Returns this README                           |
| GET   | server.address.com:5000/version     | Returns the current version of the PedalAPI   |
| GET   | server.address.com:5000/rides       | Returns all know ride ID's                    |
| GET   | server.address.com:5000/rides/{ID}  | Returns information on the specified id       |
| GET   | server.address.com:5000/kml/{ID}    | Returns a KML file of the ride                |
| GET   | server.address.com:5000/map/{ID}    | Redirects you to Google maps to view the ride |
| POST  | server.address.com:5000/rides       | Used for uploading ride information           |


Error Responses
---------------
Sending a request to the API requires a somewhat particular syntax. Error codes are available
to help you identify what went wrong in such cases. When an Error does occur, the requester will
receive both a `description` of the error as well as an error `code` that can help locate where
the issue arose.

| Code  | Description                                |
| :---: | :-----------                               |
| 100   | Non Existent URL                           |
| 200   | Ride ID does not exist on disk             |
| 300   | Request was not in JSON format             |
| 310   | 'version' field missing in POST data       |
| 311   | 'hash' field missing in POST data          |
| 312   | 'points' field missing in POST data        |
| 320   | Missing location information in point data |


Install
-------
To run this application locally, you may want to use a 
[virtual environment](VirtualEnvironment/run_locally.md) to handle dependencies.
