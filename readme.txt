Pandora's Safe Box v0.1 (JAN 2015) by kickass
http://repo.openpandora.org/?page=detail&app=psb
"...keeping your shit safe!"

PSB will backup and restore your game saves and user settings
to/from an easily accessible tar.bz2 file. It features automated
Google Drive upload, so you can grab your backups everywhere!

PSB is an advanced fork of ekianjo's Backup Saved Games App.

PSB will crawl customizable json files in your appdata folder for
installed games, emulators and user settings and allows you to
choose the contents of your automated backup.
Game saves will be handled individually on a per game basis.
This gives you full control over the backup process.
Two files will be used:
games.json - a list of games/emulators and corresponding folders
settings.json - a list of customized files/folders

You can and should customize both! I will try to update games.json
at least monthly to make sure to cover recent releases of
games and emulators. Otherwise PSB would quickly be outdated
and of no use at all. If you can't be arsed to wait for my updates
you can edit it yourself anytime you want!
settings.json should hold all the files and folders you'd like to
backup additionally (e.g. your customized .bashrc or xfce settings).
The $REAL_HOME prefix is essential to find the home folder of your
user account. Internally it will be translated to ~.
For all the Pros out there:
You can put any existing ENV variable in there
(e.g. $XDG_CONFIG_HOME)!

As of JAN 2015 Google Drive is the only supported cloud service.
Others may follow.
PSB will upload your files to a _psb folder in the root dir of your
drive account.

! There is no way for me to get a hold of your google account data !
!!               Don' be afraid of me stealing your passwords               !! 

The resulting archives may be huge in size (depending on the
number of games/emulators you selected) and that may cause
problems with the rather limited RAM of the pandora.
A swapfile may help here. It does make sense, tho, to create
individual backups (e.g. Drastic only - cuz the savegames
are huge) and rename the resulting backup file (+Drastic)
to avoid RAM shortage. Also, using small backup files means
small upload bandwith and lower risk of upload failure.
Remember that the builtin wifi sucks most of the time and may
fail out of the blue.

With a PSB backup ready, you don't start from zero the next time
a full reflash seems inevitable.

I do hope you will enjoy this little app.
It's been keeping me busy for a while :)

!! A friendly warning: !!
The restore function of PSB will literally untar any .tar.bz2
archive you throw at it to /. That's root! You may damage your
filesystem if you use a foreign archive file!
PSB will only write to dirs you already have access to, tho.
So you may be safe :)

ToDo:
- revise the upload code
- add more cloud services

Version history:

PSB v0.1 (Dec 2014):
-----------------------
gui redesign utilizing yad
rebranding and custimized logo art
further code refinement

BGS v0.2.5.0 (Aug 2014):
-----------------------
added google drive support
introduced a backup logging file (bgs.log)
backups on a per game/emulator basis
restore functionality
