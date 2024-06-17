from collections import Counter
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import defs 

import argparse
import requests


class Scraper:

    def __init__(self, api_key:str, num_players:int, number_of_games:int, region: str):
        self.api_key = api_key
        self.num_players = num_players
        self.number_of_games = number_of_games
        self.items_purchased_list = []   # List of the items purchased
        self.is_major_tier = True                # Checks whether the tier is chall/gm/master or not.
        self.region = region


    def api_urls(self, url: str)-> dict:
        """
        Method to use the api and get a response
        """
        url = url + 'api_key=' + self.api_key
        
        answer = requests.get(url)
        if answer.status_code == 200:
            return answer.json()
        else:
            print(answer.status_code)
    
        
    def get_list_of_items(self, list_of_people_puuids, stored_games):
        for players_game_container in range(self.num_players):
            for game_id in range(self.number_of_games):
                specific_game = self.api_urls(f'https://{defs.regions[self.region].value[0]}.api.riotgames.com/lol/match/v5/matches/{stored_games[players_game_container][game_id]}?')
                player = specific_game['info']['participants']
                for participant_number in range(10):
                    if list_of_people_puuids[players_game_container] in player[participant_number]['puuid']:
                        self.list_maker(participant_number, player)


    def get_list_of_games(self, list_of_puuids):
        stored_games = []
        for i in range(self.num_players):
            games = self.api_urls(f'https://{defs.regions[self.region].value[0]}.api.riotgames.com/lol/match/v5/matches/by-puuid/{list_of_puuids[i]}/ids?start=0&count={self.number_of_games}&')
            stored_games.append(games)

        self.get_list_of_items(list_of_puuids, stored_games)


    def get_summonerIDs(self, all_players_list: list)-> list:
        list_of_summonerId = []
        if self.is_major_tier:
            for player_index in range(self.num_players):
                list_of_summonerId.append(all_players_list['entries'][player_index]['summonerId'])
        else:
            for player_index in range(self.num_players):
                list_of_summonerId.append(all_players_list[player_index]['summonerId'])
        return list_of_summonerId
    

    def list_maker(self, num:int, player: list):
        """ 
        Get the id list of all the items (items.json),
        Then search that list with the id of the item purchased by the player to get the name of the item,
        Append the name of the item in a list.
        """
        get_items_list = requests.get('https://ddragon.leagueoflegends.com/cdn/14.11.1/data/en_US/item.json')
        items_list = get_items_list.json()
        for i in range(6):
            item_index = "item"+str(i)
            if item := player[num][item_index]:
                self.items_purchased_list.append(items_list['data'][str(item)]['name'])


    @staticmethod
    def list_to_dict(list_to_convert: list)-> dict:
        """
        Counts the items of the list and sorts them in a descending order, returning a dictionary.
        """
        list_to_convert_dict = Counter(list_to_convert)
        sorted_dict = dict(sorted(list_to_convert_dict.items(), key=lambda x:x[1], reverse=False))
        return sorted_dict
    

    def one_player(self, game_name:str, tag_line:str):
        player_info = self.api_urls(f'https://{defs.regions[self.region].value[0]}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?')

        return [player_info['puuid']]
    
    
    @staticmethod
    def plotting(name: str, tag: str, items: dict):
        plt.barh(items.keys(), items.values(), color = 'skyblue', height=0.5)
        plt.title(f'Item Frequency of player: {name}#{tag}.')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.tight_layout()
        plt.show()


    # Get PUUID of accounts by summonerID
    def get_puuids(self, all_players_list: list):
        """
        Provides the summonerId, the PUUID, the gameID and finally passes that information to get the items list.
        """
        list_of_summoner_Id = self.get_summonerIDs(all_players_list)
        list_of_people_puuids = []
        
        # Use summonerIDs to get PUUIDs.
        for i in range(self.num_players):
            puuid_finder = self.api_urls(f'https://{defs.regions[self.region].value[1]}.api.riotgames.com/lol/summoner/v4/summoners/{list_of_summoner_Id[i]}?')
            list_of_people_puuids.append(puuid_finder['puuid'])

        self.get_list_of_games(list_of_people_puuids)
        
    
    def tier_choice(self, tier: str, division: str):
        """
        Based on the arguments given, it will search for the appropriate API url, to get the list of the players in that given divison(and tier).
        """
        if tier in defs.tier_minor.__members__:
            chosen = f'https://{defs.regions[self.region].value[1]}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{defs.tier_minor[tier].value}/{defs.divisions[division].value}?page=1&'
            self.is_major_tier = False
            return self.api_urls(chosen)
        
        return self.api_urls(defs.tier_major[tier].value)


class Plotter:
    def __init__(self, name:str, tag:str, items: dict):
        self.name = name
        self.tag = tag
        self.items = items
    
    def plotting(self):
        plt.barh(self.items.keys(), self.items.values(), color = 'skyblue', height=0.5)
        plt.title(f'Item Frequency of player: {self.name}#{self.tag}.')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.tight_layout()
        plt.show()

    
# Arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", type=str, help="Use API key.", required=True)
parser.add_argument("-r", "--region", type=str, help='Type the region', required=True)
parser.add_argument("-t", "--tier", type=str, default= 'challenger', help="Type a tier.")
parser.add_argument("-d", "--division", type=str, help="Type a divison.", default='one')
parser.add_argument("-p", "--people", type=int, default=1, help="Enter the total amount of players to get data from.")
parser.add_argument("-v", "--volume", type=int, default=1, help="Enter the amount of games to get data from.")
parser.add_argument("-gn", "--game_name", type=str, help="enter the game name of a player.")
parser.add_argument("-tl", "--tag_line", type=str, help="enter the tag line of a player.")
args = parser.parse_args()

Starting_object = Scraper(args.key, args.people, args.volume, args.region)



if args.game_name and args.tag_line:
    single_player_list = Starting_object.one_player(args.game_name, args.tag_line)
    Starting_object.get_list_of_games(single_player_list)
    item_list = Starting_object.list_to_dict(Starting_object.items_purchased_list)
    Plot_Object = Plotter(args.game_name, args.tag_line, item_list)
    Plot_Object.plotting()

else:   
    Starting_object.get_puuids(Starting_object.tier_choice(args.tier, args.division))
    item_list = Starting_object.list_to_dict(Starting_object.items_purchased_list)
    Plot_Object = Plotter(args.tier, args.tier, item_list)
    Plot_Object.plotting()



