Since fit algorithm might take relatively long time. Therefore, sending a fit job and getting the fit results are performed in distinct messages. In both cases, the client initiates the message and the server responds.
For example, the client sends a message 'start_fit_job', and the server answers with the ID or error code. The ID is a unique number generated at the server, that identifies uniquely that message in the server's database.
When the client wishes to recieve the fit results, it sends the proper command to the server, with the ID as parameter. For example, a message with a command of 'get_job_data', and a parameter of ID.
In order to help future identification, the client either generates or uses a tag. That tag is a random word.
The message ID, therefore, must be save by both the client and the server.
The server saves the ID in the database, as a primary key,which ensures a unique ID.
The client can save this ID in several ways: server's database, file/cookie, GUI element.
To make a long story short, saving message ID with a tag
When a client sends a message to the server, an id oof that message must be kept 
