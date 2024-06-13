from collections import Counter
from enum import Enum

import argparse
import json
import requests


class Scraper:
    class tier_major(Enum):
        challenger = 'https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?'
        grandmaster = 'https://euw1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?'
        master ='https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?'

    class tier_minor(Enum):
        diamond = 'DIAMOND'
        emerald = 'EMERALD'
        gold = 'GOLD'
        silver = 'SILVER'
        bronze = 'BRONZE'
        iron = 'IRON'

    class divisions(Enum):
        one = 'I'
        two = 'II'
        three = 'III'
        four = 'IV'

    def __init__(self, api_key:str, num_players:int, number_of_games:int):
        self.api_key = api_key
        self.num_players = num_players
        self.number_of_games = number_of_games
        self.items_purchased_list = []   # List of the items purchased
        self.major = True                # Checks whether the tier is chall/gm/master or not.

    def api_urls(self, url: str)-> dict:
        """
        Method to use the api and get a response
        """
        url = url + 'api_key=' + self.api_key
        if answer := requests.get(url):
            print(answer.status_code)
            return answer.json()
    

    def get_list_of_items(self, list_of_people_puuids, stored_games):
        for players_game_container in range(self.num_players):
            for game_id in range(self.number_of_games):
                specific_game = self.api_urls(f'https://europe.api.riotgames.com/lol/match/v5/matches/{stored_games[players_game_container][game_id]}?')
                player = specific_game['info']['participants']
                for participant_number in range(10):
                    if list_of_people_puuids[players_game_container] in player[participant_number]['puuid']:
                        self.list_maker(participant_number, player)


    def get_summonerIDs(self, all_players_list: list)-> list:
        list_of_summonerId = []
        if self.major:
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
        sorted_dict = dict(sorted(list_to_convert_dict.items(), key=lambda x:x[1], reverse=True))
        return sorted_dict
    

    # Get PUUID of accounts by summonerID
    def puuids(self, all_players_list: list):
        """
        Provides the summonerId, the PUUID, the gameID and finally passes that information to get the items list.
        """
        list_of_summoner_Id = self.get_summonerIDs(all_players_list)
        list_of_people_puuids = []
        
        # Use summonerIDs to get PUUIDs.
        for i in range(self.num_players):
            puuid_finder = self.api_urls(f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/{list_of_summoner_Id[i]}?')
            list_of_people_puuids.append(puuid_finder['puuid'])

        self.get_list_of_games(list_of_people_puuids)
        
        
    def get_list_of_games(self, list_of_puuids):
        stored_games = []
        print(list_of_puuids)
        for i in range(self.num_players):
            games = self.api_urls(f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{list_of_puuids[i]}/ids?start=0&count={self.number_of_games}&')
            stored_games.append(games)

        self.get_list_of_items(list_of_puuids, stored_games)


    def tier_choice(self, tier: str, division: str):
        """
        Based on the arguments given, it will search for the appropriate API url, to get the list of the players in that given divison(and tier).
        """
        if tier in Scraper.tier_minor.__members__:
            chosen = f'https://euw1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{Scraper.tier_minor[tier].value}/{Scraper.divisions[division].value}?page=1&'
            self.major = False
            return self.api_urls(chosen)
        
        return self.api_urls(Scraper.tier_major[tier].value)


    def one_player(self, game_name:str, tag_line:str):
        player_info = self.api_urls(f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?')

        return [player_info['puuid']]


# -k : use api key 
# -t : from 0 to 8, where 0 is challenger, 1 is grandmaster, 2 is master, etc
# -d : from 1 to 4, where 1 is I, 2 is II, 3 is III, 4 is IV
# -p : default is 2, from 1 to, the upper limit changes depending on tier, as different tiers have different amount of players. (NYI)
# -v : default is 2, from 1 to 100
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", type=str, help="Use API key.", required=True)
parser.add_argument("-t", "--tier", type=str, default= 'challenger', help="Type a tier.")
parser.add_argument("-d", "--division", type=str, help="Type a divison.", default='one')
parser.add_argument("-p", "--people", type=int, default=1, help="Enter the total amount of players to get data from.")
parser.add_argument("-v", "--volume", type=int, default=1, help="Enter the amount of games to get data from.")
parser.add_argument("-gn", "--game_name", type=str, help="enter the game name of a player.")
parser.add_argument("-tl", "--tag_line", type=str, help="enter the tag line of a player.")

args = parser.parse_args()

s1 = Scraper(args.key, args.people, args.volume)

if args.game_name and args.tag_line:
    single_player_list = s1.one_player(args.game_name, args.tag_line)
    s1.get_list_of_games(single_player_list)
    print(single_player_list)

else:   
    s1.puuids(s1.tier_choice(args.tier, args.division))

item_frequency = s1.list_to_dict(s1.items_purchased_list)
for i in item_frequency:
    print(f'{i}: {item_frequency[i]}')