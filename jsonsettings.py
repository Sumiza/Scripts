"""
    Json Settings Read / Writer
"""
import json
def settingsload(filename:str):
    """
        - Read settings file from json format and return it
        - Write in any settings that are blank with option to save to file
        - Write out json file if file is missing
            - values
                - string, int, float
                - [list], {"dict":"value"}
    """
    def tryjson(value): # write str to proper type (list,int...)
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
        return value

    def settingssave():
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4)

    try:
        with open(filename, "r",encoding='utf-8') as file:
            settings = json.loads(file.read())
            change = False
            for check in settings:
                if settings[check] == "":
                    settings[check] = tryjson(input(f"Please input value for {check}: "))
                    change = True
            if change:
                answer = input("Do you want to save the changes to file? (y/n) ").casefold()
                if answer == "y":
                    settingssave()
            return settings

    except FileNotFoundError:
        print(f"{filename} not found please create it or follow along to fill it.")
        print("type .exit as key to exit or .save to save file and read settings")
        print('value can be a number, string, float, [list], {"dict":"value"} \n')
        settings = {}
        while True:
            key = input("Please write in the Key: ")
            if key == ".exit":
                exit()
            if key == ".save":
                settingssave()
                return settingsload(filename)
            value = tryjson(input("Please write the Value: "))
            settings[key] = value
            print(json.dumps(settings,indent=4))

print(settingsload("settings.json"))
