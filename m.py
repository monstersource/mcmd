##  import  ############################################################

import os
import argparse
import json

from pprint import pprint

import requests

##  read files  ########################################################


def read_txt(target):
    """read and filter a mod listing file."""
    with open(target, "r") as file:
        return [
            x for x in file.read().split("\n")
            if x != "" and not x.startswith("[")
        ]
    return False


def read_json(target):
    """read a json file."""
    with open(target, "r") as content:
        return json.load(content)
    return False


##  main  ##############################################################


def main():
    """manage curseforge minecraft mods."""

    ##  parse arguments
    parser = argparse.ArgumentParser(
        description="manage curseforge minecraft mods.")
    parser.add_argument(
        "target", help="the location of your .minecraft/mods folder.")
    args = parser.parse_args()
    pprint(args)

    ##  format arguments
    if not args.target.endswith("/"):
        args.target += "/"

    ##  f_
    f_mods = args.target + ".mods.txt"
    f_cache = args.target + ".cache.json"

    ##  handle input errors
    if not os.path.isdir(args.target):
        quit()
    if not os.path.isfile(f_mods):
        quit()

    ##  read mods list
    mods = read_txt(f_mods)
    print("mods:")
    pprint(mods)

    ##  read cache if it exists
    if os.path.isfile(f_cache):
        cache = read_json(f_cache)
    else:
        cache = {}
    print("cache:")
    pprint(cache)

    ##  get existing mod filenames
    existing = [x for x in os.listdir(args.target) if x.endswith(".jar")]
    print("existing:")
    pprint(existing)

    ##  iterate over mods
    tracked = {}
    for mod in mods:

        ##  request latest file from server
        r = requests.get(
            f"https://minecraft.curseforge.com/projects/{mod}/files/latest")
        print(r.url)

        ##  get remote filename
        filename = os.path.basename(r.url)
        print(filename)

        ##  add mod to current tracker
        tracked[mod] = filename

        ##  if the file already exists
        if filename in existing:
            print("file already exists")
        else:
            with open(args.target + filename, "wb") as target:
                print("saving new file")
                target.write(r.content)

        ##  if mod is in cache
        if mod in cache:
            print("mod in cache", end=" ")
            ##  but incorrect
            if cache[mod] != filename:
                print("but filename is wrong.", end=" ")
                if os.path.isfile(args.target + cache[mod]):
                    print("deleting incorrect file.", end=" ")
                    os.remove(args.target + cache[mod])
                cache[mod] = filename
            print("")
        ##  if mod not in cache
        else:
            print("mod not in cache")
            cache[mod] = filename

    ##  remove dead files from cache
    for mod in cache.copy():
        if mod not in tracked:
            print("mod in cache but not in mods.txt. removing from cache.")
            del cache[mod]

    ##  save new cache data
    pprint(cache)
    with open(f_cache, "w") as target:
        json.dump(cache, target, indent=4)


if __name__ == "__main__":
    main()
