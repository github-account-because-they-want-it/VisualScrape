"""
Now comes the time to think about the overall structure of my program.
I saw FMiner, and it cramps everything in one window. It doesn't seem to 
give much attention to data visualization. Probably some other external
tools can be better suited for the manipulation task, but I don't assume
my users are experts.
Now it seems my app will have 3 or 4 components:
1- the API
2- the Viewer
3- the Hatcher
4- the Launcher
is that too much?. Can it confuse the user?.
I don't think so. First, the user has nothing to do with the API.
I think the hatcher and launcher are pretty confusing names though.
or maybe not.
The launcher might be pretty sophisticated. It can allow starting of 
any number of spiders and modifying their startup settings.
It'll also make the viewer optional.
Can there be any other solutions?.
Somehow, I think this is optimal.
It'd be more magical and elegant if after the user chooses the spiders and clicks
Run or something, the choice area moves to pave the way for the viewer.
I'm thinking of a pretty, dynamic window that'll allow frequent changes
of spider parameters. Is this something I need. I think it'd be cool.
since I'll have something like content selectors, or many things about spiders
that'll need frequent changes.
Ok. Good. If I change spider parameters frequently, and I'll need to
restart a spider then, scrapy can't stop a single spider. Though the API
seems to have it.
Well it turns out scrapy is cool and stops individual spiders.
How can I support restarting spiders?
manager.restart(spider_id)
How should I layout the Hatcher, lanuncher and Viewer, if at all?
the launcher will have some a big button to create a new spider, which
will switch to the Hatcher.
Each spider button will have a checkmark and a configure spider button.
If multiple check marks are checked, all these spiders will be launched 
at the same time when clicking on Run.
There also could be something like :
File -> Launch group -> defined group1, defined group2,...
A group to the application will be a list of spider names,
which are save to disk at the configuration folder.
no. this configuration folder is for resuming...
I should have spider projects saved. Probably at a folder!
Each spider project holds information about the spider, necessary
for it's start like the spider path, and spider type, to be able to
judge whether to run it in a commandline environment. Also whether to
export it's data and where. And whether to use the viewer for it. that's it!.
The command line utility should read it's configuration, like
the place where the projects are saved, from somewhere that doesn't
depend on PySide to be available.
May I create a signal object now that has 
"""