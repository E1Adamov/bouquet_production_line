import re
from collections import defaultdict
from typing import Union, DefaultDict, List, Tuple, Dict


from src.internal.flower import Flower


class BouquetDesign:
    def __init__(self, client_input: str):
        self.client_input = client_input
        self.name: str = str()
        self.size: str = str()
        self.flower_quantity: Union[int, None] = None
        self.flowers: DefaultDict[Flower, int] = defaultdict(int)
        self.set_attributes()

    def __parse_client_input(self) -> Tuple:
        exception_msg = f"Invalid bouquet design: {self.client_input}"
        bouquet_spec_regex = re.compile(
            r"(?P<name>[A-Z])(?P<size>[L|S])(?P<flower_spec_list>(?:\d+[a-z])*)(?P<total_flower_quantity>\d*)")
        bouquet_spec_search = re.search(bouquet_spec_regex, self.client_input)

        if not bouquet_spec_search:
            raise InvalidBouquetDesign(exception_msg)

        bouquet_name = bouquet_spec_search.group('name')  # must have
        bouquet_size = bouquet_spec_search.group('size')  # must have
        flower_spec_list = bouquet_spec_search.group('flower_spec_list') or str()  # optional
        total_flower_quantity = bouquet_spec_search.group('total_flower_quantity') or str()  # optional
        found = bouquet_name + bouquet_size + flower_spec_list + total_flower_quantity

        if not bouquet_name or not bouquet_size:
            raise InvalidBouquetDesign(exception_msg)

        if total_flower_quantity:
            total_flower_quantity = int(total_flower_quantity)
            if total_flower_quantity <= 0:
                raise InvalidBouquetDesign(exception_msg)
        else:
            total_flower_quantity = None

        if not found == self.client_input or not bouquet_name or bouquet_size not in ("S", "L"):
            raise InvalidBouquetDesign(exception_msg)

        return bouquet_name, bouquet_size, total_flower_quantity, flower_spec_list

    def __get_flower_dict(self, flower_spec_list: str) -> Dict[Flower, int]:
        flower_spec_list_regex = re.compile(r'((?:\d+)(?:[a-z]))')
        flower_quantity_and_species_list: List[str] = re.findall(flower_spec_list_regex, flower_spec_list)

        def get_quantity_species(flower_spec: str) -> Tuple[str, int]:
            quantity_species_regex = r"(?P<quantity>\d+)(?P<species>\w)"
            quantity = re.search(quantity_species_regex, flower_spec).group("quantity")
            species = re.search(quantity_species_regex, flower_spec).group("species")
            return species, int(quantity)

        flower_dict: Dict[Flower, int] = dict()
        for fqas in flower_quantity_and_species_list:
            species, quantity = get_quantity_species(fqas)
            flower_dict[Flower(species=species, size=self.size)] = quantity

        if self.flower_quantity:
            flower_quantity_in_spec = sum(flower_dict.values())
            if self.flower_quantity > flower_quantity_in_spec:
                any_flower = Flower(species='A', size=self.size)
                flower_dict[any_flower] = self.flower_quantity - flower_quantity_in_spec

        return flower_dict

    def set_attributes(self):
        self.name, self.size, self.flower_quantity, flower_spec_list = self.__parse_client_input()
        self.flowers = self.__get_flower_dict(flower_spec_list)

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __getattr__(self, item):
        return getattr(self.flowers, item)


class InvalidBouquetDesign(Exception):
    pass
