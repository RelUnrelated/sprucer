# sprucer

**Version:** 1.0.1  
**Author:** RelUnrelated (<dan@relunrelated.com>)  
**License:** GNU General Public License v3.0 (GPLv3) — See the `LICENSE.md` file for details.  
**Changelog:** See the `CHANGELOG.md` file for release history and updates.  

---

## Overview
sprucer is a custom Sigil plugin designed to rearrange the (X)HTML within an EPUB file so that it is displayed in a way that more accurately depicts its semantic structure.


## Key Features

* **Options:** The plugin allows the user to select whether indentation is represented by spaces or literal tabs, and can be varied from one to eight spaces or tabs.

## Installation
This is a custom plugin, and should be installed manually through Sigil's plugin management interface.

1. Download the `sprucer_v1.0.0.zip` plugin file from the release page.
2. Open Sigil and click on the **Plugins** menu item and then **Manage Plugins**, or  click on the **Edit** menu, then the **Preferences** menu item, then select **Plugins** at the bottom of the list on the left.
3. If a previous version of **sprucer** is installed, you must uninstall it with the **Remove Plugin** button before installing the latest version.
4. Click the **Add Plugin** button on the right side of the panel.
5. Navigate to and select the `sprucer_v1.0.0.zip` file.
6. Click **Yes** to accept the security warning and install the plugin.

## Usage
Once installed, the plugin integrates seamlessly into your standard Sigil workflow.

1. Trigger the **sprucer** interface by selecting the **Plugins** menu, **Edit** submenu, and click the **sprucer** entry. Optionally, the **sprucer** plugin can be assigned to one of Sigil's plugin shortcuts in the **Manage Plugins** panel.
2. When the **sprucer settings** window appears, you will see the options for **Indentation Character**, which allows you to select either a space (U+0020) or tab (U+0009), and **Indentation Multiplier**, which allows you to select how many of these characters you wish to use for each indentation level, from 1 to 8.
3. Click the **Run Formatter** button to apply the indentation and line rules to the (X)HTML files within the open EPUB. Click **Cancel** to abort the operation.