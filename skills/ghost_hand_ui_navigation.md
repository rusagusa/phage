---
description: How to perform accurate UI navigation and button tapping using UI Automator
---

# Ghost Hand: Accurate UI Navigation Skill

When the user asks you to tap on a specific button or element on the screen (e.g., "Tap the Search button", "Click on Settings", "Open the menu"), you should **NOT** try to guess X/Y pixel coordinates visually. 

Instead, you will use the **Ghost Hand** technique, which was successfully developed in earlier versions of this architecture (like `clawbot_brain.py`).

## The Concept

Android contains a built-in accessibility tool called `uiautomator`. It allows you to dump an XML map of every single button and text field currently visible on the screen, along with their exact mathematical `[x,y]` bounds.

You will execute a sequence of shell commands to dump this XML file, read it, find the exact coordinates of the target text, and then tap it.

## The Execution Steps

Whenever you need to tap a UI element based on its text or content description, you must execute the following sequence of commands. **Do them one at a time.**

### Step 1: Dump the UI Hierarchy
First, instruct the Android system to dump the current screen's UI layout to a temporary file.

```bash
su -c "uiautomator dump /data/local/tmp/uidump.xml" || uiautomator dump /data/local/tmp/uidump.xml
```

### Step 2: Search for the Target Element
Next, you need to search that XML file for the text you want to tap (e.g., "Search"). Use `grep` or `cat` combined with your reasoning to find the XML node that contains the `text="..."` or `content-desc="..."` matching your target.

```bash
cat /data/local/tmp/uidump.xml | grep -i "YourTargetTextHere"
```

Look at the output. You are looking for a line that looks like this:
`<node index="0" text="Search" resource-id="com.example:id/search_button" class="android.widget.TextView" package="com.example" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[100,200][300,400]" />`

### Step 3: Calculate the Center Point
Once you have retrieved the XML node, look at the very end of the line for the `bounds` attribute. 
It will look like: `bounds="[x1,y1][x2,y2]"`

1. Extract the four numbers: `x1`, `y1`, `x2`, `y2`. (e.g., `bounds="[100,200][300,400]"`)
2. Calculate the exact center X coordinate: `(x1 + x2) / 2` (e.g., `(100 + 300) / 2 = 200`)
3. Calculate the exact center Y coordinate: `(y1 + y2) / 2` (e.g., `(200 + 400) / 2 = 300`)

### Step 4: Execute the Tap
Finally, use the `input tap` command with your calculated center coordinates.

```bash
input tap <center_x> <center_y>
```
*(e.g., `input tap 200 300`)*

## Summary
By following this 4-step process, you eliminate visual guessing entirely and rely on the operating system's exact mathematical layout, guaranteeing a 100% accurate tap every time.
