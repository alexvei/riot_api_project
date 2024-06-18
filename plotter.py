from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt


class Grapher:
    def __init__(self, name:str, tag:str, items: dict, index:int):
        self.name = name
        self.tag = tag
        self.items = items
        self.index = index
        self.i_b = ['Item', 'Boots']

    def store_plot(self):
        plt.subplot(1, 2, self.index)
        plt.barh(self.items.keys(), self.items.values(), color = 'skyblue', height=0.5)
        plt.title(f'{self.i_b[self.index-1]} frequency {self.name}{self.tag}.')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))


    def plot():
        plt.tight_layout()
        plt.show()