from defs import divisions, tier_major, tier_minor
from plotter import Grapher, create_and_plot
from utils import list_to_dict

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
        self.boots_purchased_list = []
        self.suburii = self.get_region_uri()


    def get_api_urls(self, url: str):
        """
        Method to use the api and get a response
        """
        url = url + 'api_key=' + self.api_key
        answer = requests.get(url)

        return answer.json() if answer.status_code == 200 else print(answer.status_code)


    def get_list_of_games(self, list_of_puuids: list)-> list:
        stored_games = []
        for i in range(self.num_players):
            games = self.get_api_urls(f'https://{self.suburii[0]}.api.riotgames.com/lol/match/v5/matches/by-puuid/{list_of_puuids[i]}/ids?start=0&count={self.number_of_games}&')
            stored_games.append(games)

        return stored_games
    

    def get_list_of_items(self, list_of_people_puuids, stored_games):
        for players_game_container in range(self.num_players):
            for game_id in range(self.number_of_games):
                specific_game = self.get_api_urls(f'https://{self.suburii[0]}.api.riotgames.com/lol/match/v5/matches/{stored_games[players_game_container][game_id]}?')
                player = specific_game['info']['participants']
                for participant_number in range(10):
                    if list_of_people_puuids[players_game_container] in player[participant_number]['puuid']:
                        self.list_maker(participant_number, player)


    # Get PUUID of accounts by summonerID
    def get_puuids(self, all_players_list: list)-> list:
        """
        Provides the summonerId, the PUUID, the gameID and finally passes that information to get the items list.
        """
        list_of_summoner_Id = self.get_summonerIDs(all_players_list)
        list_of_people_puuids = []
        
        # Use summonerIDs to get PUUIDs.
        for i in range(self.num_players):
            puuid_finder = self.get_api_urls(f'https://{self.suburii[1]}.api.riotgames.com/lol/summoner/v4/summoners/{list_of_summoner_Id[i]}?')
            list_of_people_puuids.append(puuid_finder['puuid'])
        return list_of_people_puuids
    

    def get_puuid_one_player(self, game_name:str, tag_line:str)-> list:
        player_info = self.get_api_urls(f'https://{self.suburii[0]}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?')
        # Return the puuid of the player as a list.
        # player_info is a dict by default, have to turn into a list, to be subscriptable when storing games.
        return [player_info['puuid']]
    

    def get_region_uri(self)-> tuple:
        if self.region in ["eune", "euw"]:
            suburi = "europe"
            subsub_uri = "eun1" if self.region == "eune" else "euw1"
        elif self.region == "na":
            suburi == "americas"
            subsub_uri == "na1"
        else:
            Exception("invalid region info") 
        return suburi, subsub_uri 


    def get_summonerIDs(self, all_players_list: list)-> list:
        list_of_summonerId = []
        target_list = all_players_list['entries'] if self.is_major_tier else all_players_list
        for player_index in range(self.num_players):
            list_of_summonerId.append(target_list[player_index]['summonerId'])
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
                if 'Boots' in items_list['data'][str(item)]['tags']:
                    self.boots_purchased_list.append(items_list['data'][str(item)]['name'])
                else:
                    self.items_purchased_list.append(items_list['data'][str(item)]['name'])


    def tier_choice(self, tier: str, division: str)-> dict:
        """
        Based on the arguments given, it will search for the appropriate API url, to get the list of the players in that given divison(and tier).
        """
        if tier_major.has_value(tier):
            chosen = f'https://{self.suburii[1]}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier_minor[tier].value}/{divisions[division].value}?page=1&'
            self.is_major_tier = False
            
            return self.get_api_urls(chosen)
        
        return self.get_api_urls(tier_major[tier].value)


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

data_scraper = Scraper(args.key, args.people, args.volume, args.region)

if args.game_name and args.tag_line:
    one_player_puuid = data_scraper.get_puuid_one_player(args.game_name, args.tag_line)
    games_list = data_scraper.get_list_of_games(one_player_puuid)
    data_scraper.get_list_of_items(one_player_puuid, games_list)
    placeholder_one = 'of player: ' + args.game_name
    placeholder_two = '#'+args.tag_line
else:   
    many_players_puuids = data_scraper.get_puuids(data_scraper.tier_choice(args.tier, args.division))
    games_list = data_scraper.get_list_of_games(many_players_puuids)
    data_scraper.get_list_of_items(many_players_puuids, games_list)
    placeholder_one = 'in: ' + args.tier.title()
    placeholder_two = '' if tier_major.has_value(args.tier) else args.division.title()

item_list = list_to_dict(data_scraper.items_purchased_list)
boots_list = list_to_dict(data_scraper.boots_purchased_list)
create_and_plot(placeholder_one, placeholder_two, item_list, boots_list)