---
description: How to handle incoming calls, identify callers, and make outgoing calls.
---

# Skill: Smart Call Handler

You are in charge of telephony. 

## Detecting Calls
Periodically run `termux-telephony-deviceinfo` to check 'call_state'.
- If `RINGING`: A call is coming in.
- If `OFFHOOK`: You are currently in a call.

## Identifying Callers
If a call is ringing, check the notification center `termux-notification-list`. Often the dialer will post a notification with the number or name of the caller.

## Making Calls
Use `termux-telephony-call <number>` to dial out. 

## Logic
If the user says "Call my wife", find her number in `termux-contact-list` first, then dial. Always confirm the action to the user via Voice Note.
