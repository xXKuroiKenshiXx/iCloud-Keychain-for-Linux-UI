# Command line (`icp`)

The window does all of this for you; these commands are for scripts, servers, and people who
prefer the terminal. They share the session and vault with the window. With the AppImage, run
them as `./iCloud-Keychain-x86_64.AppImage --cli <command>`.

## Sign in

```
icp login
```

This will walk you through the login: enter your Apple ID, password, and the 2FA code Apple
sends to your other devices. `icp` then asks for a **device passcode or iCloud Security Code** so
it can join your keychain.

- You're only asked for your password and 2FA code **once**. `icp` should stay signed in for a year after this.
- The passcode step is **important and can't be undone**: entering the wrong passcode too many
  times (about 10) will permanently lock your keychain recovery. One correct entry is
  perfectly safe.
- Your 2FA code and passcode are used immediately and **never saved**. Your password is kept
  **encrypted on your computer** (in your login keyring) so `icp` can stay signed in without
  asking you again - it never leaves your machine. Your access tokens and passwords are stored
  the same way.

## Browse your passwords

```
icp show
```

Opens a full-screen list - start typing to filter, **Enter** to reveal a password,
**Ctrl+P** / **Ctrl+U** to copy the password / username to the clipboard, **Esc** to quit. Add a word to search directly, or `--plain` for plain text:

```
icp show github
```

## Verification codes

If a login has an authenticator code set up in the Passwords app, `icp` picks it up too. `icp show`
lists the current 6-digit code next to the login with the seconds left before it changes, counting
down live.

## Keeping your passwords up to date

Your passwords are a snapshot, so new or changed ones need a refresh. This happens
**automatically** in the background whenever the snapshot is more than 6 hours old - you don't have
to do anything. To refresh right now:

```
icp sync
```

Syncs are paced so Apple is never hammered: at most one every 5 minutes (`--force` skips that),
and after a failure the next try waits longer (5 min, 10, 20 ... up to 6 h, or whatever Apple's
`Retry-After` asks for). Background syncs (`icp sync --background`, used by the browser helper and
timers) never sign in with your password and never trigger a verification code on your devices -
if your sign-in has expired they stop and wait for `icp login`. `icp status` shows the state.

Shared password groups you created in the Passwords app are synced too; groups someone else
shared with you are not yet.

## All commands

```
login    sign in, join your iCloud Keychain, and download your passwords
show     browse and search your passwords and Hide My Email addresses
sync     refresh your passwords now (--background for unattended runs, --force)
status   last sync, next allowed sync, whether a login is needed (--json)
diag     read-only diagnostics: zones, groups (counts only, no secrets)
logout   sign out (use --wipe-device to also forget this device)
```
