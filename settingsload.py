
import json

def settingsload(file):
    def tryjson(value):
        try:
            value = json.loads(value)
        except:
            pass
        return value

    def settingssave():
        with open(file, 'w') as f:
            json.dump(settings, f, indent=4)

    try:
        with open(file, "r",encoding='utf-8') as f:
            settings = json.loads(f.read())
            change = False
            for check in settings:
                if settings[check] == "":
                    settings[check] = tryjson(input(f"please input value for {check}: "))
                    change = True
            if change:
                answer = input("Do you want to save the changes to file? (y/n) ").casefold()
                if answer == "y":
                    settingssave()
            return settings
    except FileNotFoundError:
        print(f"{file} not found please create it or follow along to fill it.")
        print("type .exit as key to exit or .save to save file and exit")
        print("value can be a number, string, float, list or dict\n")
        settings = {}
        while True:
            key = input("Please write in the key: ")
            if key == ".exit":
                exit()
            if key == ".save":
                settingssave()
                return settings
            value = tryjson(input("Please input the Value: "))
            settings[key] = value
            print(json.dumps(settings,indent=6))

print(settingsload("settings.json"))


