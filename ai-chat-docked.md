new feature:

create new feature branch feature/aichatdock

this will be a pro feature (try to keep files in the pro folder and behind paywall/paid)
when enabled (if user clicks the checkbox for it in the pro features section) it will add a docked window to the right where it can have unlimited or many ai chat tabs open where it allows them to paste/send the context block+prompt etc right to AI models and chat with them right in the app instead of having to use web sites and paste it on those.
We can use the existing settings panel/window for the ai models/api endpoints/etc that already exists for the ai rewrite button

there will be a 2nd generate context button that will instead of copying to clipboard, it will send it to the chosen ai chat's/models. There should be new tab button to open more chat tabs, and a way to choose ai model/provider for each one. there should be a checkbox somewhere in each of the open ones that is for allowing / accepting context block if the user wants to send it to some of the models. Like if they have 7 tabs open, and they want to ask a question/with context to 3 of them, they can just checkmark the ones they want to get the question+context..

we will NOT use a web browser type thing to display the chat's because its too bloated, eats ram. Part of the selling point of the app is it doesn't eat ram and its pretty small/lean.

I want to do custom rendering of markdown so if a model replies with different headings sizes etc it will show those in different colors but all headings same size. code blocks can use the same font and same libraries etc that the preview window uses to show code files.

write a plan to implement this, and try to code most of it and i can just test later, or do big phases or - you can do TDD, but you need to be able to start the app with a timer that auto-closes, and i have a cli tool that will take screenshots of apps:

usage: appsnap [-h] [-l] [-a DIR] [-o PATH] [-t N] [-j] [-v] [window_name]

Fast Windows screenshot tool for AI coding agents

positional arguments:
window_name Window title to search for (supports fuzzy matching)

options:
-h, --help show this help message and exit
-l, --list List all capturable windows and exit
-a, --all DIR Capture all windows to specified directory
-o, --output PATH Output file path (default: temp directory with timestamp)
-t, --threshold N Fuzzy match threshold 0-100 (default: 70, lower = more lenient)
-j, --json Output result as JSON with path and metadata
-v, --version Show version and exit

Example: appsnap "aicodeprep-gui" --output screenshot.png

but coding agents keep getting stuck if they run the app, and then have no way to close it, so it will sit forever. If you are going to test put a --timer 10s option or similar, where it will close by itself after 10s.
