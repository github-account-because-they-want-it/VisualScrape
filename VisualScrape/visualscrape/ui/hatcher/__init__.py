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
May I create a signal object now that has ... no
How do you plan to pull that GUI together?.
I am not very decided about it's nature, yet.
First, let's work on the hatcher. It should support all the features of my API.
It shall have a browser, with an area to enter the url to start from.
a load progress will be fine and cool, since now it's frightening to watch it.
the hatcher will watch the user and create Form or Url objects as necessary.
Then the item page. I want to be different. The hatcher will have a checkmark of some sort
to mark a page as the main page. What kind of checkmark?.I intend it to be an overlay
on the browser. Or a checkmark inside the browsing box, like what google has up there in the
bar. Let's try that now.
Ok, I got a lineedit with an Icon, what's next?. 
How to mark a damn page as a main page?. WTF!. It can't be that complex. But I think
it's stupid that idea. I think it'd be better to make at at the bottom right of the browser. Nice try, though.
I can use them both. I think Now at least I got a preliminary icon to be used to. I think I have it
now.
the user will navigate and when clicks on that thing, He'll be asked a couple of qustions.
He'll be asked to choose an example item link and an optional navigation page (assume it'll
be chosen for now). If I ask him before, It's kinda more likely I'll have no way to cancel the choice.
I'll have a menu option to reset choices.
Ok. I think I need an elegant message widget. Instead of the status bar. It it should play it's geometry
on showing and hiding. DONE!
How can I handle content selectors in the UI?
It can be a good feature when nothing else works. Since it requires the user intervention.
So the user clicks on something, the browser fails to find anything, so it brings up some kind
of dialog to the user to intervene.
So that's how to handle content selectors. Ok.
How to handle image scraping?. The user right-clicks an image and selects if he wants
to download it (which will get it displayed on the viewer), or just scrape it's url.
Image selection is usually successful in the browser, so it shouldn't be a problem to check
them if the user clicks twice. Selection should happen outside the GUI thread because sometimes
it blocks and it'll make the app look a bit irresponsive.
What about page actions?. The user can do some clicks on the item page. And he can select
one or more items after that. The API supports multiple actions I think, but I didn't test.
So. Take care of the case when the user navigates back to the same page. Don't handle
it as a new page.
Each click the user performs will be recorded in a table on the left. (or better, the bottom).
there will be 2 tables, one for the key-value data, the other for page actions.
If the user hovers over the key/value in the table, it'd be nice to be highlighted in the page,
so she can make sure things are AOK. Maybe not the way back, from the browser to the table, not 
to drive her mad.
Am I finished?. I think yea!
Now It's time to talk more!. the gui could record scrolling. How can that be handled?.
How should the action table be layouted?. 
It could be a click action, followed by a select after action
or it could be a scroll action, also followd by a select.
What are the properties of a scroll?. The distance?. The scrolled-to element?. Or to the end of page.
what to wait for after the scroll?. Any specific new content?. The data after the scroll could be similar to
existing data, or it could be different.
I'm thinking of an action wizard. Since there maybe many choices.
But that seems like a mostly empty wizard. That seems like a very involved GUI.
Just a dialog. Ok, just a dialog. No, It'll be a wizard. 
Ok. The action wizard will allow a field to be populated. Whether to add it to an
existing field, or to a new field.
I think I'm done. Where should I start?.
I can create the Action menu, and layout with the browser and tables. I think a table view will be
good, since it has an icon role or something like that.
I think I can enhance the current state of element selection by 2 ways:
1- descending to children in findByText
2- Having an API TableSelector which scrapes every text node in the table. or the first 2 columns
First, me browsing other people's advanced stuff and sometimes boring, fills me with
 both boredom and fear. I've learnt along my programming path till now. Sometimes I care
too much about the end results. Will it be good, competitive. Some tools are even free of charge.
Why am I doing this, afterall?. if not for money. What else do I have to do, anyway. I have things
I want to learn, but I need to apply somewhere. Having this app in-place will help.
It can also be a good advertisement of my abilities. So I'm not losing. Have fun.
Now for the table selectors. How'll you go about that?
it seems now that tables can actually be more than 2 columns.though what?.
I always used tables in a key-value relationship. And it has always been fine.
There are some table styles it seems. Not one style:
1- Headers (keys) at top with values in <td>s some rows may have a rowspan property for grouping. 
2- Headers left and values right (which is the type of most commercial tables).
These are the table types I know of. The problem is with the tables with non-even column count. These
may not be much, but it's good to consider them.
So. There will be a table selector in the API. This one won't concern itself with
figuring out the table type. This will be done at the user/GUI level.
The table selectors should be passed on through a preprocessing stage, right?
Why?. to get the key/value from them. No. Keys and values won't be available until we are on the
page. The table selection will be kept dynamic, to avoid extra rows.
"""