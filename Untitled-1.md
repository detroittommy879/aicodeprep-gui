actually, can you put that menu option back in the Help menu but just change it so instead, it just opens a popup with a email link to open their email app to email me at tom@wuu73.org ? just have a message that says put Bug, Problem with ..whatever the issue is, or Suggestion etc in subject line and to just email me? Also the way that the app sends to my custom endpoints (where I have a docker container that tries to record a little info/analytics from .../aicp-metrics/ ) is not robost enough - i think it should be buffering the data for a while and then sending in chunks but with code that will retry but in the background / in a safe non blocking way. Also i wanted to upgrade the analytics data that is sent, add some stuff, like:

the folder email-collector/ is the analytics system, its super basic, when i modify this version I will just copy it to my ubuntu server (arm64) and shutdown the old container, and then docker compose up the new / fresh one. I want to modify/add some stuff to it:

Track:
(add these)
free vs paid user - have it send the status of free/pro anytime it sends some data
what they have the language set to (english? chinese, italian, arabic, etc) when they are using it/generate context

feature usage by feature:
file selection UI
saved per-project selections
prompt before/after
duplicate prompt trick
do they turn on / use the enable file preview window?
flow graph / multi-LLM routing - do they ever click the box to turn this on? do they ever go through with actually using it to send the context block to multiple llms? if so, which ai models were used?
do they use the open repo feature?
did they click to enable the ai chat feature? do they use it after turning it on?

Disable/remove the AI rewrite button and model select from the UI (below the clear button for the prompt box) but move the settings button (to the right of AI Rewrite and Select model... ) for models since it is used by the ai chat, over to the AI chat's settings button (currently, when you click that, it just tells you to click the other settings but it is too confusing)

Lets get rid of the everything is free popup etc, and instead just give everyone 20 days free after installing it - maybe change the popup to telling them about this

--
