# RaspberryPiSensor

Dette projekt indeholder en socket client og en socket server, begge skrevet i python.

server.py køres på en raspberry pi, som periodisk indsamler data(humidity, temp, tid),
som ved forbindelse fra en client socket sender dette data tilbage

## Opsætning

Vi har flash'et en Raspberry Pi OS ISO til et SD kort med et program kaldet Raspberry Pi Imager. Gennem raspberry Pi Imager har vi opsat ssh og wifi.

For at finde vores raspberry pi på det lokale netværk, har vi anvendt nmap.

```sh
nmap -sn 10.200.130.1/24
```

Vi anvender bibliotekerne dht11 og GPIO til opsætningen af sensoren og raspberry pi'en.

Til serveren anvender vi et native library i python kaldet socket:

```py
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((IP_SCHOOL, PORT))
        server.listen(BACKLOG)
        while True:
            server, address = server.accept()
            print(f"connection from {address} has been made at time: {get_time()}")
            start_new_thread(handle_connection, (server,))
```

De 2 parameter der gives i socket.socket er for at fortælle socket serveren at den skal anvende IPv4 addresser og TCP protokollen. Backlog er antallet indgående forbindelser der kan stå på vent.

Serveren lytter efter indgående forbindelser og starter en ny tråd hvor "samtalen" mellem klient og server fortsætter:

```py
def handle_connection(client_socket):
    global is_recording
    msg = client_socket.recv(1024).decode("utf-8")
    if msg == "get":
        send_data(client_socket)

def send_data(client_socket):
    client_socket.send(bytes(
        json.dumps(data), "utf-8"))
```

Når klienten sender en anmodning, bliver beskeden konverteret fra bytes til tekst og anmodningen bliver håndteret. Når klienten anmoder om data, vil serverens data blive converteret til json format (javascript object notation) og blive sendt som bytes til klienten.

For at overføre server scriptet til vores raspberry pi anvender vi:

```sh
scp ~/server.py pi@IP:~/server/server.py
```

For at sikre os at serveren kører ved opstart har vi installeret en process manager kaldet pm2:

```bash
npm install pm2 -g
pm2 start script.sh
pm2 startup
pm2 save
```

Klienten er skrevet i java og fremstiller data fra serverens sensor i en graf.

## Protokol

Valget af protokol er landet på TCP, da UDP ikke bringer nogle fordele der er egnet til vores formål. UDP er overlegen i hastighed, men det kommer på bekostningen af stabilitet og fejlhåndtering. Da overførelses hastigheden af den data vi skal håndtere ikke er vigtigt, så var valget nemt.
TCP kan garantere levering af data, gensende pakker hvis de bliver tabt under forsendelse og fejlhåndterer dataen, derfor er det vores valg til dette projekt.

## Overvejelser af features / forbedringer:

- Generel fejlhåndtering
- TimeOut/FailSafe
- Multiple Connection
- Håndtering af socket connection
- Dato
- Database til håndtering af målinger over længere tid/dage.

## Konklusion

Igennem projektet konkludere vi at vores forløb har gået godt, da vi ingen mangler har og at programmet fungere i forhold til opstillede krav. Dog ved vi at vi har nogle forbedringer samt overvejelser af features vi ved kunne gøre programmet bedre og meget mere optimalt.
