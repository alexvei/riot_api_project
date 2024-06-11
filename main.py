from collections import Counter

import argparse
import json
import requests


class Scraper:

    items_purchased_list = []
    major = True
    def __init__(self, api_key:str):
        self.api_key = api_key


    def api_urls(self, url: str)-> dict:
        url = url + 'api_key=' + self.api_key
        if answer := requests.get(url):
            return answer.json()
    

    def tier_choice(self, tier: int, division: int):
        tier_major = {
        0: 'https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?', 
        1: 'https://euw1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?', 
        2: 'https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?'}
        tier_minors = {3: 'DIAMOND', 4: 'EMERALD', 5: 'GOLD', 6: 'SILVER', 7: 'BRONZE' ,8: 'IRON'}
        divisions = {1: 'I', 2: 'II', 3: 'III', 4: 'IV',}
        if tier >= 3:
            chosen = f'https://euw1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier_minors[tier]}/{divisions[division]}?page=1&'
            self.major = False
            return self.api_urls(chosen)
        
        print(tier_major[tier])
        return self.api_urls(tier_major[tier])
    

    @staticmethod
    def list_maker(num: int, player: list):
        get_items_list = requests.get('https://ddragon.leagueoflegends.com/cdn/14.11.1/data/en_US/item.json')
        items_list = get_items_list.json()
        for i in range(6):
            item_index = "item"+str(i)
            if item := player[num][item_index]:
                Scraper.items_purchased_list.append(items_list['data'][str(item)]['name'])
        return True


    @staticmethod
    def list_sorter(list_to_sort: list)-> dict:
        list_to_sort_dict = Counter(list_to_sort)
        sorted_dict = sorted(list_to_sort_dict.items(), key=lambda x:x[1], reverse=True)
        return dict(sorted_dict)


    # Get PUUID of accounts by summonerID
    def puuids(self, num_players: int, number_of_games: int, all_players_list: list):
        list_of_people_puuids = []
        list_of_summonerId = []
        stored_games = []

        if self.major:
            for player_index in range(num_players):
                list_of_summonerId.append(all_players_list['entries'][player_index]['summonerId'])
        else:
            for player_index in range(num_players):
                list_of_summonerId.append(all_players_list[player_index]['summonerId'])


        for i in range(num_players):
            puuid_finder = self.api_urls(f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/{list_of_summonerId[i]}?')
            list_of_people_puuids.append(puuid_finder['puuid'])
            games = self.api_urls(f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{list_of_people_puuids[i]}/ids?start=0&count={number_of_games}&')
            stored_games.append(games)

        # Append the LIST of games of a player in a LIST.
        for players_game_container in range(num_players):
            for game_id in range(number_of_games):
                specific_game = self.api_urls(f'https://europe.api.riotgames.com/lol/match/v5/matches/{stored_games[players_game_container][game_id]}?')
                player = specific_game['info']['participants']

                # Each game contains 10 different collections, 1 for each player/champion. Look for the player's PUUID in that list of 10 collections to find which collection belongs to that player. Then go in that collection look for the items and save them in a list.
                for participant_number in range(10):
                    if list_of_people_puuids[players_game_container] in player[participant_number]['puuid']:
                        self.list_maker(participant_number, player)


# -k : use api key 
# -t : from 0 to 8, where 0 is challenger, 1 is grandmaster, 2 is master, etc
# -d : from 1 to 4, where 1 is I, 2 is II, 3 is III, 4 is IV
# -p : default is 2, from 1 to, the upper limit changes depending on tier, as different tiers have different amount of players. (NYI)
# -v : default is 2, from 1 to 100
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", type=str, help="Use API key.", required=True)
parser.add_argument("-t", "--tier", type=int, help="Select tier [0-2].", required=True)
parser.add_argument("-d", "--division", type=int, help="Select divison [0-3].", default=1)
parser.add_argument("-p", "--people", type=int, default=2, help="Enter the total amount of players to get data from.")
parser.add_argument("-v", "--volume", type=int, default=2, help="Enter the amount of games to get data from.")
args = parser.parse_args()

s1 = Scraper(args.key)

s1.puuids(args.people, args.volume, s1.tier_choice(args.tier, args.division))

item_frequency = s1.list_sorter(Scraper.items_purchased_list)
for i in item_frequency:
    print(f'{i}: {item_frequency[i]}')

