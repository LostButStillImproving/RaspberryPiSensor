# RaspberryPiSensor

Dette projekt indeholder en socket client og en socket server, begge skrevet i Python.

server.py køres på en raspberry pi, som periodisk indsamler data(humidity, temp, tid),
som ved forbindelse fra en client socket sender dette data tilbage.

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

# Client
Vi har bygget en client til at tale sammen med vores server i java. [link til client repo](https://github.com/LostButStillImproving/SensorMeSilly)

Programmet er opdelt i 4 pakker: controllers, model, network og util.

## Controller:
Indeholder Controller klassen, som implementerer MeasureementObserver interfacen, dette er for at observere det data der bliver hentet fra serveren, og vise dette som en graf.
## model:
Indeholder ViewModelMeasurement, som implementerer ObserverableMeasurement, denne klasse er Controllerens kontaktflade med resten af applikationen og indeholder funktionalitet som at bede ServiceRequest klassen om at hente data fra serveren i samarbejde med ClientConnector klassen. Der benyttes i ViewModelMeasurement-klassen en single threaded executorservice, til at lave at et kald til ServiceRequest klassen hvert sekund, således at data fra server modtages hvert sekond. I vores implementation laves der en NY socket forbindelse i stedet for at den samme holdes åbent, dette er muligvis ikke den optimale måde at gøre dette på. Denne hentede data bliver som nævnt før, observeret og fremvist af controller klassen.
```java
public void startListening() {
        if (executorService.isShutdown()) {
            executorService = Executors.newSingleThreadScheduledExecutor();
        }
        executorService.scheduleAtFixedRate(() -> {
                    try {
                        Measurement measurement = getMeasurement();
                        listOfObservers.forEach(
                                observer -> observer.update(measurement));
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }, 0, 1,
                        TimeUnit.SECONDS);
    }
```
## Network:
Indeholder de tidligere beskrevet klasser ClientConnector og ServiceRequest.

ClientConnector skaber en socketforbindelse således:
```java
public static Socket getConnection() throws IOException {

        if (socket == null) {

            return new Socket(SCHOOL_IP, PORT);
        }
        return socket;
    }
```
Hvor SCHOOL_IP, og PORT er konstanter.

ServiceRequest klassen indeholder forskellelige metoder alt afhængig af hvad der ønskes at gøres med sereven, f.eks kan intervallet hvorved serveren måler temp/hum indstilles via clienten ved hjælp af følgende:

```java
public void setSensorInterval(int seconds) {
        out.printf("interval%s", seconds);
        out.flush();
        out.close();
    }
```
Ligeledes, hvis der skal hentes data fra serveren, gøres det via:
```java
public String getData() throws IOException {
        out.printf("get%s", "");
        out.flush();
        return in.readLine();
    }
```
Der skrives til outputstreamet, hvorefter serverens respons aflæses af inputstreamet og returneres til videre databehandling. 

## Util
Da dataen modtages som en json formatteret UTF-8 string, er der brug for at konvertere denne til det dataobjekt det repræsentere på clientside, dette gøres via util klassen, som indeholder følgende:
```java
public static Measurement jsonToMeasurement(String json) throws JsonProcessingException {
        ObjectMapper objectMapper = new ObjectMapper();
        Map<String, Object> map = objectMapper.readValue(json, new TypeReference<>() {
        });

        String time = (String) map.get("time");
        double temperature = Double.parseDouble(String.valueOf(map.get("temperature")));
        double humidity = Double.parseDouble(String.valueOf(map.get("humidity")));

        return new Measurement(time, temperature, humidity);
    }
```
Der benyttes jackson core til at omdanne json strengen til et <String, Object> map, hvorfra vi hiver de relevante felter ud (tid, temp, fugtighed), og benytter disse til at skabe et Measurement instans. Som controlleren bruger til at fremvise dataen på en graf.


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
