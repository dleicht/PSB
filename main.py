'''
Copyright (c) 2015 Dominik Leicht <domi.leicht@gmail.com> aka kickass

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy and modify the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

The Software is designed to be freeware. It may not be used, offered or sold
as a commercial product in any way.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''
import os, glob, subprocess, json, pprint, PyZenity, itertools, tarfile
from datetime import datetime
from sys import exit
from pprint import pprint
from pydrive.auth import GoogleAuth, CheckAuth
from pydrive.drive import GoogleDrive


# variables galore:
appdatapath = os.getenv('APPDATADIR')
mypath = os.getenv('HOME')
archivename = "PSB_{0}.tar.bz2".format(datetime.today().strftime("%Y-%m-%d_%H%M%S"))
yadcmd = mypath + "/yad"
psblogo = mypath + "/PandoraBoxTrans_200_flames.png"
readme = mypath + "/readme.txt"
logfile = appdatapath + "/bgs.log"
games_jsonfile = appdatapath + "/games.json"
settings_jsonfile = appdatapath + "/settings.json"
browserdict = {"firefox": ["firefox", "/usr/share/applications/hdonk_firefox_001#0.desktop"],
                "qupzilla": ["qupzilla", "/usr/share/applications/qupzilla-app#0.desktop"],
                "babypanda": ["babypanda", "/usr/share/applications/babypanda-app#0.desktop"]}
yad_error = ' --image="gtk-dialog-error" --text="Whoa, something went terribly wrong!\nHere is an error msg for you:\n\n{0}" --title="PSB" --button="gtk-ok" --window-icon='+psblogo
yad_warn = ' --image="gtk-dialog-warning" --text="{0}" --title="PSB" --button="gtk-ok" --window-icon='+psblogo
yad_general = ' --text="{0}" --title="PSB" --button="gtk-ok" --button="gtk-cancel" --window-icon='+psblogo
yad_info = ' --image="gtk-dialog-info" --text="{0}" --title="PSB" --button="gtk-ok" --window-icon='+psblogo
gauth = None
drive = None

def add2log(afile, dirs):
    try:
        with open(logfile, 'a') as handle:
            handle.write(str(afile) + ": " + str(dirs) + "\n")
        print "\nLog entry added..."
    except Exception as err:
        print err

def thanksandgoodnight():
    infowindow = subprocess.check_output([yadcmd+yad_info.format("All done\nThanks for using PSB :)")], shell=True)
    print "All done\nThanks for using PSB :)"

def checkbgsfolder(): # check for a _psb folder in the root dir of the gdrive account. if none is found it will be created and it's fileid returned.
    folderthere = None
    folderinlist = None
    while folderthere is not True:
	    try:
	        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	        for file1 in file_list: # Auto-iterate through all files that match this query
	            if "_psb" in file1['title'].encode('utf8'):
	                folderid = str(file1['id'].encode('utf8'))
	                folderinlist = True
	            else:
	                pass
	    except Exception as err:
	        print err
	        errwindow = subprocess.check_output([yadcmd+yad_error.format(err)], shell=True)
	        psb()
	    if folderinlist is True:
	        print "_psb folder found!"
	        print "_psb folder id: " + folderid
	        folderthere = True
	    else:
	        print "_psb folder not found!"
	        newdir = drive.CreateFile({'title': '_psb', 'mimeType': 'application/vnd.google-apps.folder'}) # in the gdrive api folders are just files with a specific mime-type
	        newdir.Upload()
	        print "Created _psb folder..."
	        print "Re-checking for the folder to get the id..."
    else:
		return folderid

def upload_backup(afile):
    print "\nChecking available JScript capable browsers:\n"
    browsers = parsedesktopfile(checkbrowsers(browserdict))
    print "\nFound the following browsers:"
    pprint(browsers)
    if browsers == "":
        errwindow = subprocess.check_output([yadcmd+yad_warn.format("None of the required browsers seem to be installed!\nCan not upload the backup!")], shell=True)
        psb()
    print "\nChecking connectivity:"
    if internet_on() != 0:
        errwindow = subprocess.check_output([yadcmd+yad_warn.format("Can not reach the interwebs!\nCan not upload the backup!")], shell=True)
        psb()
    print "Ready to upload "+afile
    global gauth
    if not gauth or gauth.access_token_expired is True: # Check if GoogleAuth() has not been invoked before and if the Google Drive Access Token has expired. If so: initiate GoogleAuth()
        print "Google Auth needed..."
        gauth = GoogleAuth()
        print "Creating a local webserver and auto handle authentication..."
        try:
            gauth.LocalWebserverAuth(browsercmd=browsers[0][2]) # Creates local webserver and auto handles authentication
            global drive
            drive = GoogleDrive(gauth)
        except Exception as err:
            print err
            errwindow = subprocess.check_output([yadcmd+yad_error.format(err)], shell=True)
            psb()
        upload_backup(afile)
    else:
        print "gauth.access_token_expired = " + str(gauth.access_token_expired)
        print "Google Auth already handled..."
        fid = checkbgsfolder()
        newfile = drive.CreateFile({'title': archivename, "parents": [{"kind": "drive#fileLink", "id": fid}]})
        print "Now uploading: " + archivename + "\nto folder: " + str(fid)
        newfile.SetContentFile(afile)
        try:
            proc = PyZenity.Progress(text='Uploading ' + archivename, title='PSB', auto_close=True, pulsate=True, no_cancel=True, window_icon=psblogo)
            proc(10)
            newfile.Upload()
            print "upload done!"
            proc(100)
        except Exception as err:
            print err
            errwindow = subprocess.check_output([yadcmd+yad_error.format(err)], shell=True)
            psb()

def psb():
    mainmenu = psb_gui_mainwindow() #mainmenu[gui returncode, path to archive, gamesaves, usersettings, gdrive]
    if mainmenu[0] == 2:
        if mainmenu[2] == "FALSE" and mainmenu[3] == "FALSE":
            print "No backup choice was made."
            warnwindow = subprocess.check_output([yadcmd+yad_warn.format("Please choose games and/or settings to backup!")], shell=True)
            psb()
        elif mainmenu[2] == "TRUE" and mainmenu[3] == "FALSE": # backup game saves only
            backupfile = makearchivefile(backupspecific(read_json(games_jsonfile)), mainmenu[1])
            add2log(backupfile[0], backupfile[1])
            if mainmenu[4] == "TRUE":
                upload_backup(backupfile[0])
                thanksandgoodnight()
                psb()
            else:
                thanksandgoodnight()
                psb()
        elif mainmenu[3] == "TRUE" and mainmenu[2] == "FALSE": # backup settings only
            backupfile = makearchivefile(check4filefolder(read_json(settings_jsonfile)), mainmenu[1])
            add2log(backupfile[0], backupfile[1])
            if mainmenu[4] == "TRUE":
                upload_backup(backupfile[0])
                thanksandgoodnight()
                psb()
            else:
                thanksandgoodnight()
                psb()
        elif mainmenu[2] == "TRUE" and mainmenu[3] == "TRUE": # backup both
            glist = backupspecific(read_json(games_jsonfile))
            slist = check4filefolder(read_json(settings_jsonfile))
            print "Will now join games and settings folders..."
            gslist = glist + slist
            backupfile = makearchivefile(gslist, mainmenu[1])
            add2log(backupfile[0], backupfile[1])
            if mainmenu[4] == "TRUE":
                upload_backup(backupfile[0])
                thanksandgoodnight()
                psb()
            else:
                thanksandgoodnight()
                psb()
    elif mainmenu[0] == 4:
        if mainmenu[1] != "(null)":
            untarbackup(mainmenu[1])
        else:
            errwindow = subprocess.check_output([yadcmd+yad_error.format("You need to specify a backup file to restore from!")], shell=True)
            print "You need to specify a backup file to restore from!"
            psb()

def checkbrowsers(browserlist): # check a list of .desktop files for existance and add items to a list of existing browsers.
    availablebrowsers = []
    for val in browserlist.itervalues():
        if os.path.isfile(val[1]):
            availablebrowsers.append(val)
    return availablebrowsers

def parsedesktopfile(browserlist): # parse the existing browsers for their respective pnd_run commands.
    browsercmds = []
    for item in browserlist:
        try:
            with open(item[1], "r") as handle:
                for line in handle:
                    if line.startswith("Exec"):
                        execline = line.strip("Exec=")
                        print "Exec line found - containing the following cmd path:"
                        print execline
                        l = []
                        l.append(item[0])
                        l.append(item[1])
                        l.append(execline.strip('\n\r'))
                        browsercmds.append(l)
                    else:
                        pass
        except Exception as err:
            print err
    return browsercmds # returns a list of browsername[0], path of desktopfile[1], pnd_run command[2]

def psb_gui_mainwindow():
    print "Welcome to PSB v0.1\nReturned results of psb_gui_mainwindow():\n"
    proc1 = subprocess.Popen([yadcmd+' --plug=5 --tabnum=1 --form --field="Backup Dir:DIR" --field="Game Saves:CHK" --field="User Settings:CHK" --field="GDrive Upload:CHK"'], shell=True, stdout=subprocess.PIPE)
    
    proc2 = subprocess.Popen([yadcmd+' --plug=5 --tabnum=2 --form --field="Restore From:FL"'], shell=True, stdout=subprocess.PIPE)
    
    proc3 = subprocess.Popen([yadcmd+' --plug=5 --tabnum=3 --text-info --fontname="normal 9" --filename='+readme], shell=True)
    
    try:
        mainwindow = subprocess.Popen([yadcmd+' --image='+psblogo+' --center --notebook --width=660 --key=5 --tab="Backup" --tab="Restore" --tab="About" --title="PSB" --window-icon='+psblogo+' --button="Backup:2" --button="Restore:4" --button="Exit:6"'], shell=True, stdout=subprocess.PIPE)
        mainwindow.communicate()
        print "returncode was: "+str(mainwindow.returncode)
    except subprocess.CalledProcessError as e:
        print e
    finally:
        backup_values = [mainwindow.returncode] #if psb_gui_mainwindow[0] == 2, then it's a backup
        for i in proc1.communicate()[0].strip("\n").split("|"):
            backup_values.append(i) #proc1_values [psb_mode, dir2save, game saves backup, user settings backup, gdrive upload]
        
        restore_values = [mainwindow.returncode] #if psb_gui_mainwindow[0] == 4, then it's a restore
        for i in proc2.communicate()[0].strip("\n").split("|"):
            restore_values.append(i) #proc2_values [psb_mode, file2restore from]
        if mainwindow.returncode == 6:
            print "Exited by user."
            exit()
        elif mainwindow.returncode == 252:
            print "Exited by user."
            exit()
    #Backup routine starts here:
        elif mainwindow.returncode == 2:
            print "Backup routine started with the following options:\n"
            print "Backup dir:"
            print backup_values[1]
            print "Game saves backup: "+str(backup_values[2])
            print "User settings backup: "+str(backup_values[3])
            print "Gdrive upload: "+str(backup_values[4])
            return backup_values
    #Restore routine starts here
        elif mainwindow.returncode == 4:
            print "Restore routine started with the following options:\n"
            print "Backup file:"
            print restore_values[1]
            return restore_values

def read_json(jfile):
    print "trying to read json file: "+str(jfile)
    try:
        with open(jfile, "r") as handle:
            list2check=json.load(handle)
            print "json read!"
            return list2check
    except Exception as err:
        print err
        errwindow = subprocess.check_output([yadcmd+yad_error.format(err)], shell=True)
        psb()

def checkprogram(progname, directory): #returns folder if the PND is found in one of the appsfolder directory or "" if not found
    appsfolder = ['menu', 'desktop', 'apps']
    found = 0
    for folder in appsfolder:
        if os.path.isfile("/media/{0}/pandora/{1}/{2}".format(directory, folder, progname)) == True:
            print "Found " + progname + " in " + folder + " in " + directory
            found += 1
        if found == 0:
            return ""
        else:
            return folder

def checkappdata(appdatafolder, directory): #checks if the related appfolder exists
    if os.path.isdir("/media/{0}/pandora/appdata/{1}".format(directory, appdatafolder)) == True:
        return True
    else:
        return False

def backupspecific(gameslist): # crawl games.json for path/filenames with gamesaves and ask for the ones to be archived
    directories = os.listdir("/media") # get the global directories
    print "directories list:"
    print directories
    if "hdd" in directories:
        directories.remove("hdd")
        print "removed hdd"
    if "ram" in directories:
        directories.remove("ram")
        print "removed ram"
    for directory in directories:
        if directory.startswith("."):
            directories.remove(directory)
            print "removed "+directory
    print "\nWill now crawl "+str(directories)+" for games/emulators:\n"
    programsfound = []
    prog_folder_list = []
    for game in gameslist:
        directorytobackup = []
        prog_folder_couple = []
        for topdirectory in directories:
            workingfolder = checkprogram(game[0], topdirectory)
            if workingfolder != "":
                prog_folder_couple.append(game[0]) # add the program .pnd name to a list of program+[folders] couple list (on a per program basis - so the program name and corresponding folders will be coupled properly
                #print "working folder is " + workingfolder #confirm the top level working folder under /media/xx/pandora/PAF  - it is not used after expect for path
                if checkappdata(game[1], topdirectory) == False:
                    print "the program " + game[0] + ".pnd does not have a appdata folder so far."
                else:
                    directoriesinappfolder = os.listdir(("/media/{0}/pandora/appdata/{1}".format(topdirectory, game[1]))) # special case of ALLFOLDER: where everything is to backup in the said folder
                    if game[2] == '*ALLFOLDER*':
                        print "*ALLFOLDER* found for "+game[0]
                        directorytobackup.append(("/media/{0}/pandora/appdata/{1}").format(topdirectory, game[1]))
                    else:
                        #marks folders to save
                        for onefolder in directoriesinappfolder:
                            for foldertobackup in game[2]:
                                if onefolder == foldertobackup:
                                    print game[0] + ":found folder " + onefolder + " to backup"
                                    directorytobackup.append(("/media/{0}/pandora/appdata/{1}/{2}").format(topdirectory, game[1], onefolder)) #add the path worklist to backup where we will give the final instructions to zip in the end
                                #need to build functions for files as well
                        for filetobackup in game[3]:
                            result = []
                            result = glob.glob("/media/{0}/pandora/appdata/{1}/{2}".format(topdirectory, game[1], filetobackup))
                            if result != []:
                                for resultat in result:
                                    directorytobackup.append(resultat)
        if directorytobackup != []: # check listoftemplates for programs, if directorytobackup is NOT empty, the program seems to be available for backup
            prog_folder_couple.append(directorytobackup) # add the folders to that same couple list
            prog_folder_list.append(prog_folder_couple) # add the couple list to a list of all couples
        else:
            pass
    
    bgs_dict = dict(prog_folder_list) # now this is really cool: using a dictionary with prognames as keys, we can easily ask for prognames to be backuped and parse the dictionary for the corresponding values to automatically get the right folders!
    print "\nDictionary of games:folders available for backup (bgs_dict):\n"
    pprint(bgs_dict)
    gamelist = []
    glist = []
    for item in bgs_dict.keys():
        gamelist.append("")
        gamelist.append(item)
        glist.append(gamelist)
        gamelist = []
    print "\nNow asking for items to backup...\n"
    a = PyZenity.List(["#","Game"], text="Found the following games/emulators.\nPlease select which you'd like to backup:", title="PSB", boolstyle="checklist", window_icon=psblogo, height=400, editable=False, select_col=None, sep='|', data=glist)
    pprint(a)
    if a == None:
        print "Canceled by user..."
        psb()
    elif a == [""]:
        print "No choice was made."
        warnwindow = subprocess.check_output([yadcmd+yad_warn.format("Please choose at least one game to backup!")], shell=True)
        psb()
    else:
        chosendirstobackup_ = []
        for item in a:
            chosendirstobackup_.append(bgs_dict[item]) # parse the dictionary for values(folders) of the chosen items(prognames).
            chosendirstobackup = list(itertools.chain(*chosendirstobackup_)) # proper usage of itertools to flatten a nested list of lists :) note there's two lists here: chosendirstobackup_ and chosendirstobackup
        return chosendirstobackup

def internet_on():
    nstat = os.system('ping -c 1 8.8.8.8')
    return nstat

def makearchivefile(folders, pathtoarchive): # build the actual archive from given path/filenames, return [archivename, folders]
    if folders == []:
		errwindow = subprocess.check_output([yadcmd+yad_error.format("No valid list entries to build a backup from!\nCancelling...")], shell=True)
		print "No valid list entries to build a backup from!\nCancelling..."
		psb()
    else:
	    print "\nWill now start makearchivefile() with the following folders:"
	    pprint(folders)
	    archivefile = pathtoarchive + "/" + archivename
	    sizeofarchive = 0
	    print "\nChosen archivefile:\n" + archivefile
	    if os.path.isfile(archivefile) == True:
	        print "Careful, an archive with the same name already exists."
	    try:
	        archive = tarfile.open(archivefile, "w:bz2")
	    except Exception as err:
	        print err
	        errwindow = subprocess.check_output([yadcmd+yad_error.format(err)], shell=True)
	        exit()
	    #define nb of directories to backup
	    nbdirectoriestobackup = float(len(folders))
	    print nbdirectoriestobackup
	    #there will probably be bugs inside this part... need to check it out!!
	    # kickass: funny, you imported PyZenity on purpose to make things easier, but decided to not use it in this case. i wonder why...
	    #cmd = 'zenity --progress --text="Backing Up Games Saves..." --auto-close'
	    #proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	    proc = PyZenity.Progress(title="PSB", text="Packing up:\n"+folders[0], auto_close=True, no_cancel=True, window_icon=psblogo)
	    n = 0.0
	    for folder in folders:
	        n += 1
	        print "added " + folder
	        progress = int(100 * (float(n / nbdirectoriestobackup)))
	        print progress
	        progress -= 1 # So the progressbar won't close as soon as 100% is reached (as the last task also may take a while...)
	        proc(progress, folder)
	        archive.add(folder)
	    try:
	        archive.close()
	        proc(100)
	    except Exception as err:
	        print err
	        errwindow = subprocess.check_output([yadcmd+yad_error.format(err)], shell=True)
	        exit()
	    sizeofarchive = int((os.path.getsize(archivefile)) / (1024 * 1024))
	    a = subprocess.check_output([yadcmd+yad_warn.format("Backup completed as:\n" + archivefile + "\n\nThe file size is:\n" + str(sizeofarchive) + " Mb.")], shell=True)
	    return [archivefile, folders]

def untarbackup(file2untar):
    print "Will now untar: "+str(file2untar)
    a = subprocess.check_output([yadcmd+yad_general.format("You seriously should ONLY\nrestore PSB made backups with this tool.\nYou risk data loss and/or disk damage otherwise.\n\nYou've been warned.")], shell=True)
    try:
		tar = tarfile.open(file2untar, mode="r:bz2")
		proc = PyZenity.Progress(text='Restoring from ' + file2untar, title='PSB', auto_close=True, pulsate=True, no_cancel=True, window_icon=psblogo)
		print "\n\nTrying to extract the archive to / ...\n\n"
		proc(10)
		for tarinfo in tar:
			print tarinfo.name, "is", tarinfo.size, "bytes in size and is",
			if tarinfo.isreg():
				print "a regular file."
			elif tarinfo.isdir():
				print "a directory."
			else:
				print "something else."
			tar.extract(path="/",member=tarinfo)
		tar.close()
		proc(100)
    except Exception as err:
        errwindow = subprocess.check_output([yadcmd+yad_error.format(err)], shell=True)
        psb()
    finally:
        thanksandgoodnight()
        psb()

def check4filefolder(alist):
    if alist == []:
        errwindow = subprocess.check_output([yadcmd+yad_error.format("No valid list entries to build a backup from!\nCancelling...")], shell=True)
        print "No valid list entries to build a backup from!\nCancelling..."
        psb()
    else:
	    checked_list = []
	    print "parsing a list for valid entries..."
	    pprint(alist)
	    for item in alist:
	        item = os.path.expandvars(item) # $REAL_HOME points to the user's real home dir! This should so find it's way into the libpnd wiki!!
	        print item
	        if os.path.exists(item):
	            checked_list.append(item)
	            print "added "+item+" as a valid entry..."
	        else:
	            print item+" is not a valid folder or file, skipped."
	    return checked_list

# start the app
psb()
