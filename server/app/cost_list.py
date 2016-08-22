import csv
import itertools
from googlemapsAtoB import GoogleMapsAtoB

"""
Constructor Inputs:
  addresses - a list of addresses (or coordinates)
  api_key - a Google Maps API key
"""
class CostList:
    def __init__(self, addresses, api_key):
        self.addresses = addresses
        self.api_key = api_key

    def get_cost_list(self):
        # Ideally, we want the itertools.permutation function instead since
        # itertools.combinations assumes the time between point A and point B is
        # symmetric (that is, the time from A to B is the same as B to A).
        # Using the itertools.permutation function, however, approximately doubles
        # the amount of time it takes to retrieve the needed information from the
        # Google Maps API (makes sense because we are doubling the pairs of addresses).
        # Hence, we will make this simplifying assumption for now until we find
        # a solution that makes using permutations more efficient.
        address_pairs = itertools.combinations(self.addresses, 2)
        return [(a, b, GoogleMapsAtoB(a, b, self.api_key).get_time()) for a, b in address_pairs]

    """
    input: the name of the csv file.
    output: a csv file of all the combinations of pairs of addresses and their
        associated cost (in this case, time).
    """
    def to_csv(self, csv_name, delimiter='*'):
        cost_list_to_csv = self.cost_list()

        with open(csv_name, 'wb') as csvfile:
            output = csv.writer(csvfile, delimiter=delimiter)
            output.writerow(["address1", "address2", "cost"])
            for a, b, cost in cost_list_to_csv:
                output.writerow([a, b, cost])
