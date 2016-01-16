# Kaco RS485 Doc

Python library to retrieve information from Kaco inverters.


## Example

A small example is provided in the file called `example.py`.

Basic usage is also described below:
```
import kacors485

K = kacors485.KacoRS485('/dev/ttyUSB0')

#read inverter with address 1
data = K.readInverterAndParse(1)

K.close()

#show result
print(data)
```

The output of the example above can be e.g.:
```
{
    'checksum': {
        'description': 'Pruefsumme',
        'name': 'checksum',
        'value': 'as'
    },
    'counter_h': {
        'description': 'Zaehler Stunden',
        'name': 'counter_h',
        'value': '8:46'
    },
    'e_all': {
        'description': 'Gesamtenergie in 0.1kWH',
        'name': 'e_all',
        'value': '581'
    },
    'e_day': {
        'description': 'Tagesenergie in Wh',
        'name': 'e_day',
        'value': '4184'
    },
    'i_ac': {
        'description': 'Netz Strom',
        'name': 'i_ac',
        'value': '24.90'
    },
    'i_dc': {
        'description': 'Generator Strom',
        'name': 'i_dc',
        'value': '10.17'
    },
    'last_command_sent': {
        'description': 'Adresse & Fernsteuerbefehl',
        'name': 'last_command_sent',
        'value': '*013'
    },
    'no_idea': {
        'description': 'Zaehler der Hochzaehlt, ka was',
        'name': 'no_idea',
        'value': '42'
    },
    'p_ac': {
        'description': 'Einspeiseleistung',
        'name': 'p_ac',
        'value': '5720'
    },
    'p_dc': {
        'description': 'Generator Leistung',
        'name': 'p_dc',
        'value': '5958'
    },
    'p_top': {
        'description': 'Spitzenleistung in W',
        'name': 'p_top',
        'value': '2286'
    },
    'run_all': {
        'description': 'Betriebsstunden gesamt in h',
        'name': 'run_all',
        'value': '11:04'
    },
    'run_today': {
        'description': 'Betriebsstunden heute in h',
        'name': 'run_today',
        'value': '11:04'
    },
    'status': {
        'description': 'Status des Wechselrichters',
        'name': 'status',
        'value': '4'
    },
    'temp': {
        'description': 'Geraetetemperatur',
        'name': 'temp',
        'value': '36'
    },
    'type': {
        'description': 'Wechselrichter Typ',
        'name': 'type',
        'value': '9600I'
    },
    'u_ac': {
        'description': 'Netz Spannung',
        'name': 'u_ac',
        'value': '229.5'
    },
    'u_dc': {
        'description': 'Generator Spannung',
        'name': 'u_dc',
        'value': '585.9'
    },
}
```

## Testing

For unit tests run `$ ./runtest.sh`.


### End to End Testing

In order to test the application with a serial interface, we will simulate one. On Ubuntu 14.04, the following will create a serial interface:

```
sudo apt-get install socat

#create serial terminal input and output
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

now, on another terminal, one can run the input with the mockinverter script. Replace the serial interface, which the one you just created:
```
python mockinverter.py /dev/pts/29
```

and in another terminal the example python program
```
python example.py /dev/pts/28

#or to run with pdb debugger (press c to continue)
python -mpdb example.py /dev/pts/28
```

## Development Info

### Website with Source Information

http://techcrawler.riedme.de/2011/09/25/dd-wrt-logger-per-rs-485-an-kaco-wechselrichter/


### Data Protocoll

send #xxy\r with
xx: number of inverter and y: command:
```
echo -e "#010\r" > /dev/usb/tts/0
```

answer for 0:
```
#Adresse & Fernsteuerbefehl	Status	Generator-spannung	Generator-strom	Generator-leistung	Netz-spannung	Netz-strom	Einspeise-leistung	Geräte-temperatur	Tages-energie	WR Kürzel prüfsumme
*010	4	585.9	10.17	5958	229.5	24.90	5720	36	17614	9600I dx
```

answer for 3:
```
<LF>*013 2286 4184 42 581 8:46 11:04 11:04<CR>
```
Mit den Feldern:
- 2286 der Spitzenleistung [W] entspricht (5 Stellen)
- 4184 der Tagesenergie [Wh] entspricht (6 Stellen, identischer Wert wie bei Kommando "0")
- 42 ein Zähler ist der hochzählt (6 Stellen) (habe noch keine Ahnung was das ist)
- 581 der Gesammtenregie in [1/10*kWh] entspricht (6 Stellen)
- 8:46 dem "Zähler Stunden" entspricht (6:2 Stellen)
- 11:04 den "Betriebsstunden heute" entsprechen (6:2 Stellen) (Vermutung !!)
- 11:04 den "Betriebsstunden gesammt" wohl entsprechen (6:2 Stellen) (Vermutung !!)
