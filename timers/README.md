# Timers Help

Start a timer countdown.<br/><br/>All purpose timer countdown.

# timer
 - Usage: `[p]timer <duration> [title] `
 - Restricted to: `MOD`
 - Checks: `guild_only`

Timer.

## timer cancel
 - Usage: `[p]timer cancel [message=None] `

Cancel a timer.

## timer end
 - Usage: `[p]timer end [message=None] `

Manually end a timer.

## timer list
 - Usage: `[p]timer list `

See all the active timers in this guild.

# timerset
 - Usage: `[p]timerset `
 - Restricted to: `ADMIN`
 - Checks: `guild_only`

Configure timer settings.

## timerset resetcog
 - Usage: `[p]timerset resetcog `
 - Restricted to: `BOT_OWNER`

Reset this cogs whole config.

## timerset maxduration
 - Usage: `[p]timerset maxduration <maxduration> `
 - Restricted to: `BOT_OWNER`
 - Aliases: `md`

Set the maximum duration a timer can countdown.

## timerset autodelete
 - Usage: `[p]timerset autodelete `
 - Aliases: `autodel`

Toggle auto deletion on timer command completion.

## timerset showsettings
 - Usage: `[p]timerset showsettings `
 - Aliases: `ss`

Show current timer settings.

## timerset buttoncolour
 - Usage: `[p]timerset buttoncolour <button_type> [colour_type=None] `
 - Aliases: `buttoncolor`

Change the timer ended or started button colour.<br/><br/>Pass without colour to check current set colour.<br/>Pass reset in colour to reset.

## timerset notifymembers
 - Usage: `[p]timerset notifymembers `

Toggle whether to notify members when the timer ends or not.

## timerset emoji
 - Usage: `[p]timerset emoji [emoji=None] `

Change or reset the timer emoji.

## timerset resetguild
 - Usage: `[p]timerset resetguild `

Reset this guild's timer settings.