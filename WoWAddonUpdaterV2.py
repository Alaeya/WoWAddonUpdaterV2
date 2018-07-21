import zipfile, configparser
from io import *
from os.path import isfile
import packages.requests as requests
from threading import Thread
import pickle

num_upt = 0
addon_count = 0
update_threads = []


def confirm_exit():
    input('\nPress the Enter key to exit')
    exit(0)


# Site splitter
def find_ziploc(addonpage):
    # Curse
    if addonpage.startswith('https://mods.curse.com/addons/wow/'):
        return curse('https://www.curseforge.com/wow/addons/' + addonpage.split('/')[-1])

    elif addonpage.startswith('https://www.curseforge.com/wow/addons/'):
        return curse(addonpage)

    # Curse Project
    elif addonpage.startswith('https://wow.curseforge.com/projects/'):
        return curse('https://www.curseforge.com/wow/addons/' + addonpage.split('/')[-1])

    # Tukui
    elif addonpage.startswith('https://www.tukui.org/download.php?ui='):
        return tukui(addonpage)

    # Invalid page
    else:
        print('Invalid addon page.')


def get_current_version(addonpage):
    # Curse
    if addonpage.startswith('https://mods.curse.com/addons/wow/'):
        return get_curse_version('https://www.curseforge.com/wow/addons/' + addonpage.split('/')[-1])

    # Curse Project
    elif addonpage.startswith('https://wow.curseforge.com/projects/'):
        return get_curse_version('https://www.curseforge.com/wow/addons/' + addonpage.split('/')[-1])

    # Curse 2
    elif addonpage.startswith('https://www.curseforge.com/wow/addons/'):
        return get_curse_version(addonpage)

    # Tukui
    elif addonpage.startswith('https://www.tukui.org/download.php?ui='):
        return get_tukui_version(addonpage)

    # Invalid page
    else:
        print('Invalid addon page.')


def curse(addonpage):
    try:
        page = requests.get(addonpage + '/download')
        content_string = str(page.content)
        index_of_ziploc = content_string.find('download__link') + 22  # Will be the index of the first char of the url
        end_quote = content_string.find('"', index_of_ziploc)  # Will be the index of the ending quote after the url
        return 'https://www.curseforge.com' + content_string[index_of_ziploc:end_quote]
    except Exception:
        print('Failed to find downloadable zip file for addon. Skipping...\n')
        return ''


def get_curse_version(addonpage):
    try:
        page = requests.get(addonpage + '/files')
        content_string = str(page.content)
        date_added_pos = content_string.find('<abbr class="tip standard-date standard-datetime" title="') + 57
        date_added = content_string[date_added_pos:date_added_pos + 19]
        return date_added.replace(" ", ".", 2)

    except Exception:
        print('Failed to find version number for: ' + addonpage)
        return ''


def curse_project(addonpage):
    try:
        page = requests.get(addonpage + '/files/latest')
        content_string = str(page.content)
        index_of_ziploc = content_string.find('download__link') + 22  # Will be the index of the first char of the url
        end_quote = content_string.find('"', index_of_ziploc)  # Will be the index of the ending quote after the url
        return page
    except Exception:
        print('Failed to find downloadable zip file for addon. Skipping...\n')
        return ''


def get_curse_project_version(addonpage):
    try:
        page = requests.get(addonpage + '/files')
        content_string = str(page.content)
        date_added_pos = content_string.find('<abbr class="tip standard-date standard-datetime" title="') + 57
        date_added = content_string[date_added_pos:date_added_pos + 19]
        return date_added
    except Exception:
        print('Failed to find version number for: ' + addonpage)
        return ''


def tukui(addonpage):
    try:
        page = requests.get(addonpage)
        addon_name = addonpage.replace('https://www.tukui.org/download.php?ui=', '')
        content_string = str(page.content)
        index_of_cur_ver = content_string.find('The current version')
        index_of_ver = content_string.find('">', index_of_cur_ver) + 2
        end_tag = content_string.find('</b>', index_of_cur_ver)
        version = content_string[index_of_ver:end_tag]
        return 'https://www.tukui.org/downloads/' + addon_name + '-' + version + '.zip'
    except Exception:
        print('Failed to find downloadable zip file for addon. Skipping...\n')
        return ''


def get_tukui_version(addonpage):
    try:
        page = requests.get(addonpage)
        content_string = str(page.content)
        date_added_pos = content_string.find('and was updated on') + 38
        date_added = content_string[date_added_pos:date_added_pos + 10]
        return date_added.replace("-", ".")
    except Exception:
        print('Failed to find version number for: ' + addonpage)
        return ''


##################################################################################################################################################################################################################
##################################################################################################################################################################################################################
##################################################################################################################################################################################################################


class AddonUpdater:
    def __init__(self):
        print('')
        print("----- AddonUpdaterV2 started ----- \n")
        # Read config file
        if not isfile('config.ini'):
            print('Failed to read configuration file. Are you sure there is a file called "config.ini"?\n')
            confirm_exit()

        config = configparser.ConfigParser()
        config.read('config.ini')

        try:
            self.WOW_ADDON_LOCATION = config['WOW ADDON UPDATER']['WoW Addon Location']
            self.ADDON_LIST_FILE = config['WOW ADDON UPDATER']['Addon List File']
            self.INSTALLED_VERSION_FILE = config['WOW ADDON UPDATER']['Installed Versions File']
            self.AUTO_CLOSE = config['WOW ADDON UPDATER']['Close Automatically When Completed']
        except Exception:
            print('Failed to parse configuration file. Are you sure it is formatted correctly?\n')
            confirm_exit()

        if not isfile(self.ADDON_LIST_FILE):
            print('Failed to read addon list file. Are you sure the file exists?\n')
            confirm_exit()

        global installed_versions_array
        with open(r"InstalledVersion.txt", "rb") as f:
            installed_versions_array = pickle.load(f)


        return

    def update(self):

        print("##  Addon-Name:                         Last Update:                        Status:\n")
        print("                                        MM.DD.YYYY HH:MM:SS")
        with open(self.ADDON_LIST_FILE, "r") as fin:
            global addon_count
            global num_upt
            global update_threads

            for line in fin:
                line = line.rstrip('\n')
                if line.startswith('#'):
                    continue
                elif line == '':
                    continue
                else:
                    addon_count = addon_count + 1

                    u = Thread(target=self.addon_check, args=(line, addon_count,))

                    update_threads.append(u)

            for x in update_threads:
                x.start()

            for x in update_threads:
                x.join()
        print("\n\nUpdate finished: \nUpdated/installed   %s   out of   %s   Addons" % (num_upt, addon_count))

        with open(r"InstalledVersion.txt", "wb") as output_file:
            pickle.dump(installed_versions_array, output_file)

        if self.AUTO_CLOSE == 'False':
            confirm_exit()

    def addon_check(self, line, addon_count2):
        cur_addon_name = self.get_addon_name(line)
        cur_version = get_current_version(line)
        if cur_version is None:
            cur_version = 'Not Available'
        ins_version = self.get_installed_version(line)

        if not cur_version == ins_version:
            self.addon_update(addon_count2, cur_addon_name, cur_version, line)
            if cur_version is not '':
                self.set_installed_version(line, cur_version)
        else:
            if addon_count2 < 10:
                addon_count22 = "0" + str(addon_count2)
            else:
                addon_count22 = addon_count2
            print_addon_name = str(str(addon_count22) + ') ' + cur_addon_name)
            len_name = len(print_addon_name)
            while len_name in range(0, 40):
                print_addon_name = print_addon_name + ' '
                len_name = len_name + 1
            print_version_name = cur_version
            len_version = len(print_version_name)
            while len_version in range(0, 35):
                print_version_name = print_version_name + ' '
                len_version = len_version + 1
            print(print_addon_name + print_version_name + ' is up to date.', )

    def addon_update(self, addon_count3, cur_addon_name, cur_version, line):
        if addon_count3 < 10:
            addon_count33 = "0" + str(addon_count3)
        else:
            addon_count33 = addon_count3
        print_addon_name = str(str(addon_count33) + ') ' + cur_addon_name)
        len_name = len(print_addon_name)
        while len_name in range(0, 40):
            print_addon_name = print_addon_name + ' '
            len_name = len_name + 1
        print_version_name = cur_version
        len_version = len(print_version_name)
        while len_version in range(0, 35):
            print_version_name = print_version_name + ' '
            len_version = len_version + 1
        print(print_addon_name + print_version_name + ' installing...', )

        ziploc = find_ziploc(line)
        self.get_addon(ziploc)
        global num_upt
        num_upt += 1

    def get_addon(self, ziploc):
        if ziploc == '':
            return
        try:
            r = requests.get(ziploc, stream=True)
            z = zipfile.ZipFile(BytesIO(r.content))
            z.extractall(self.WOW_ADDON_LOCATION)
        except Exception:
            print('Failed to download or extract zip file for addon. Skipping...\n')
            return

    def get_addon_name(self, addonpage):
        addon_name = addonpage.replace('https://mods.curse.com/addons/wow/', '')
        addon_name = addon_name.replace('https://www.curseforge.com/wow/addons/', '')
        addon_name = addon_name.replace('https://wow.curseforge.com/projects/', '')
        addon_name = addon_name.replace('https://www.tukui.org/download.php?ui=', '')
        addon_name = addon_name.replace('-', ' ')
        try:
            return addon_name
        except Exception:
            return 'Name not found'

    def get_installed_version(self, addonpage):
        global installed_versions_array
        addon_name = addonpage.replace('https://mods.curse.com/addons/wow/', '')
        addon_name = addon_name.replace('https://www.curseforge.com/wow/addons/', '')
        addon_name = addon_name.replace('https://wow.curseforge.com/projects/', '')
        addon_name = addon_name.replace('https://www.tukui.org/download.php?ui=', '')
        installed_version = "not available"
        for i in range(len(installed_versions_array)):
            if installed_versions_array[i][0] == addon_name:
                installed_version = installed_versions_array[i][1]
                break
        try:
            return installed_version
        except Exception:
            return 'version not found'

    def set_installed_version(self, addonpage, cur_version):
        global installed_versions_array
        addon_name = addonpage.replace('https://mods.curse.com/addons/wow/', '')
        addon_name = addon_name.replace('https://www.curseforge.com/wow/addons/', '')
        addon_name = addon_name.replace('https://wow.curseforge.com/projects/', '')
        addon_name = addon_name.replace('https://www.tukui.org/download.php?ui=', '')
        found = False
        for i in range(len(installed_versions_array)):
            if installed_versions_array[i][0] == addon_name:
                installed_versions_array[i][1] = cur_version
                found = True
                break
        if not found:
            installed_versions_array.append([addon_name, cur_version])



def main():
    addonupdater = AddonUpdater()
    addonupdater.update()
    return


if __name__ == "__main__":
    # execute only if run as a script
    main()
