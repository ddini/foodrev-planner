import csv
from itertools import combinations
from googlemapsAtoB import GoogleMapsAtoB

"""
input: a list of addresses and the name of the csv file.
output: a csv file of all the combinations of pairs of addresses and their
    associated cost (in this case, time).
"""
class CostList:
    def __init__(self, addresses, api_key):
        self.addresses = addresses
        self.api_key = api_key

    def cost_list(self):
        address_pairs = combinations(self.addresses, 2)
        return [(a, b, GoogleMapsAtoB(a, b, self.api_key).get_time()) for a, b in address_pairs]

    def to_csv(self, csv_name):
        cost_list_to_csv = self.cost_list()

        with open(csv_name, 'wb') as csvfile:
            output = csv.writer(csvfile)
            output.writerow(["address1", "address2", "cost"])
            for a, b, cost in cost_list_to_csv:
                output.writerow([a, b, cost])
