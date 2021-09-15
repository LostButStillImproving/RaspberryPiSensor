# RaspberryPiSensor

Dette projekt indeholder en socket client og en socket server, begge skrevet i python.

server.py køres på en raspberry pi, som periodisk indsamler data(humidity, temp, tid),
som ved forbindelse fra en client socket sender dette data tilbage


### Overvejelser af features / forbedringer:
- håndtering af socket connection
- Dato
- Database til håndtering af målinger over længere tid/dage.
