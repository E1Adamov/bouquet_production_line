## Bouquet production line

### Prerequisites:
- Python 3.8.2 or higher
- internet connection for installing 3rd party packages
- Docker

### Installation
Run `python3 setup.py install`

### Running
1. Server:  
   Run `docker-compose build && docker-compose up`  
2. Client  
   - Run `python3 cli_client.py` for manual input
   - Or run `python3 cli_client.py test.txt` to run the provided test automatically

### Todo list
- improve logic to pick least needs flowers from stock when we can choose any
- implement database for warehouse and other operations
- for better scalability put all objects (input service, production, warehouse, shipping dept) into separate containers
- investigate if message broker is needed
