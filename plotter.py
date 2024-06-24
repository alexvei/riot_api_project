from matplotlib.ticker import MaxNLocator
from utils import list_to_dict

import matplotlib.pyplot as plt


class Grapher:
    def __init__(self, name:str, tag:str, items: dict, index:int):
        self.name = name
        self.tag = tag
        self.items = items
        self.index = index
        self.items_boots = ['Item', 'Boots']

    def store_plot(self):
        plt.subplot(1, 2, self.index)
        plt.barh(list(self.items.keys()), list(self.items.values()), color = 'skyblue', height=0.5)
        plt.title(f'{self.items_boots[self.index-1]} frequency {self.name}{self.tag}.')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))


    def plot(self):
        plt.tight_layout()
        plt.show()


def create_and_plot(name, tag, items_list, boots_list):
    graphers = [
        Grapher(name, tag, items_list, 1),
        Grapher(name, tag, boots_list, 2)]

    for grapher in graphers:
        grapher.store_plot()

    graphers[0].plot()

