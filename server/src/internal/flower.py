class Flower:
    def __init__(self, species: str = None, size: str = None, client_input: str = None):
        self.species = species
        self.size = size
        self.process_client_input(client_input)

    def process_client_input(self, client_input: str):
        if client_input is not None:
            try:
                self.species = client_input[0]
                self.size = client_input[1]
            except Exception:
                raise InvalidFlower(f"Invalid flower: {client_input}")

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size: str):
        if size is not None and size not in ('S', 'L'):
            raise NotImplementedError(f"Flower size {size} is not implemented")

        self.__size = size

    @property
    def species(self):
        return self.__species

    @species.setter
    def species(self, species: str):
        if species == 'A':
            pass
        elif species is not None and not 97 <= ord(species) <= 122:
            raise NotImplementedError(f"Flower species {species} is not implemented")

        self.__species = species

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self.species, self.size))


class InvalidFlower(Exception):
    pass
