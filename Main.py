import requests
from urllib.parse import urlencode
import time
import json
import sys


class VkApp:
    APP_ID = 6126927
    VERSION = "5.67"
    KEY = "g63AiqLhELfIKqIxaLbv"
    pool = requests.Session()

    def make_request(self, URL, param):
        response = self.pool.get(URL, params=param)
        if "error" in response.json().keys():
            time.sleep(0.5)
            response = self.pool.get(URL, params=param)
        return response



class VkOauth(VkApp):
    def oauth_link(self):
        oauth_adr = "https://oauth.vk.com/authorize"
        auth_data = {
            "client_id": self.APP_ID,
            "scope": "friends groups",
            "response_type": "token",
            "v": self.VERSION
        }
        return "?".join((oauth_adr, urlencode(auth_data)))

    def get_token(self):
        token = input("Welcome to the dimploma app.\nPlease, input it here: \n{}\n".format(self.oauth_link()))
        return token


class VkAppGroups(VkApp):
    TOKEN = "5dfd6b0dee902310df772082421968f4c06443abecbc082a8440cb18910a56daca73ac8d04b25154a1128"

    def get_freind_l(self, user_id):
        URL = "https://api.vk.com/method/friends.get"
        param = {
            "access_token": self.TOKEN,
            "v": self.VERSION,
            "user_id": user_id
        }
        response = self.make_request(URL, param)

        return response.json()["response"]["items"]

    def collect_groups(self, user_id):
        URL = "https://api.vk.com/method/groups.get"
        param = {
            "access_token": self.TOKEN,
            "v": self.VERSION,
            "user_id": user_id
        }
        response = self.make_request(URL,param)

        return response.json()

    def collect_group_data(self, groups_list):
        chunks = [groups_list[x:x + 100] for x in range(0, len(groups_list), 100)]
        groups_list_full = []
        for n, chunk in enumerate(chunks):
            print("Getting groups info... {} out of {} ready".format(100*n, len(groups_list)))
            URL = "https://api.vk.com/method/groups.getById"
            param = {
                "access_token": self.TOKEN,
                "v": self.VERSION,
                "group_ids": ",".join([str(x) for x in chunk]),
                "fields": "members_count"
            }
            response = self.make_request(URL, param)
            for item in response.json()["response"]:
                new_group_entry = {}
                new_group_entry["name"] = item["name"]
                new_group_entry["gid"] = item["id"]
                if "members_count" in item.keys():
                    new_group_entry["members_count"] = item["members_count"]
                else:
                    new_group_entry["members_count"] = "Not available"
                groups_list_full.append(new_group_entry)
        return groups_list_full

    def collect_groups_friends(self):
        user_id = self.startme()
        print("Getting friends list...")
        friend_list = self.get_freind_l(user_id)
        print("Collecting your groups...")
        my_groups = set(self.collect_groups(user_id)["response"]["items"])
        for n, friend in enumerate(friend_list):
            print("Checked {} friends out of {}".format(n + 1, len(friend_list)))
            # Проверяем был ли пользователь удалён или заблокирован
            if "error" in self.collect_groups(friend).keys():
                pass
            else:
                non_unique = my_groups & set(self.collect_groups(friend)["response"]["items"])
                my_groups -= non_unique
            time.sleep(0.5)
        return list(my_groups)

    def startme(self):
        if len(sys.argv) > 1:
            subject_one_id = sys.argv[1]
        else:
            subject_one_id = input("Input an ID or name\n")
        subject_one_id = subject_one_id.strip()
        if subject_one_id.isdigit() == False:
            print("Getting your ID")
            URL = "https://api.vk.com/method/users.get"
            param = {
                "access_token": self.TOKEN,
                "v": self.VERSION,
                "user_ids": subject_one_id
            }
            response = self.make_request(URL, param)
            print(response.json())
            subject_one_id = response.json()["response"][0]["id"]
        return subject_one_id


def save_file(my_data):
    with open("result.json", "w", encoding="cp1251") as fp:
        json.dump(my_data, fp)


def main():
    VkGroup = VkAppGroups()
    a = VkGroup.collect_groups_friends()
    a = VkGroup.collect_group_data(a)
    save_file(a)

while __name__ == "__main__":
    main()
