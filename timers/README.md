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

Show running timers from this guild.

# timerset
 - Usage: `[p]timerset `
 - Restricted to: `ADMIN`

Configure timer settings.

## timerset notifymembers
 - Usage: `[p]timerset notifymembers `

Toggle whether to notify members when the timer ends or not.

## timerset buttoncolour
 - Usage: `[p]timerset buttoncolour <button_type> [colour_type=None] `
 - Aliases: `buttoncolor`

Change the timer ended or started button colour.<br/><br/>Pass without colour to check current set colour.<br/>Pass reset in colour to reset.

## timerset resetguild
 - Usage: `[p]timerset resetguild `

Reset this guild's timer settings.

## timerset showsettings
 - Usage: `[p]timerset showsettings `
 - Aliases: `ss`

Show current timer settings.

## timerset maxduration
 - Usage: `[p]timerset maxduration <maxduration> `
 - Restricted to: `BOT_OWNER`
 - Aliases: `md`

Set the maximum duration a timer can countdown.

## timerset emoji
 - Usage: `[p]timerset emoji [emoji=None] `

Change or reset the timer emoji.

## timerset resetcog
 - Usage: `[p]timerset resetcog `
 - Restricted to: `BOT_OWNER`

Reset this cogs whole config.