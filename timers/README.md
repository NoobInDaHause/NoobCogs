# Timers Help

Start a timer countdown.<br/><br/>All purpose timer countdown.

# timer
 - Usage: `[p]timer <duration> [title] `
 - Restricted to: `MOD`
 - Checks: `guild_only`

Timer.

## timer end
 - Usage: `[p]timer end [message=None] `

Manually end a timer.

## timer cancel
 - Usage: `[p]timer cancel [message=None] `

Cancel a timer.

## timer list
 - Usage: `[p]timer list `

Show running timers from this guild.

# timerset
 - Usage: `[p]timerset `
 - Restricted to: `ADMIN`

Configure timer settings.

## timerset resetguild
 - Usage: `[p]timerset resetguild `

Reset this guild's timer settings.

## timerset resetcog
 - Usage: `[p]timerset resetcog `
 - Restricted to: `BOT_OWNER`

Reset this cogs whole config.

## timerset notifymembers
 - Usage: `[p]timerset notifymembers `

Toggle whether to notify members when the timer ends or not.

## timerset emoji
 - Usage: `[p]timerset emoji [emoji=None] `

Change or reset the timer emoji.

## timerset maxduration
 - Usage: `[p]timerset maxduration <maxduration> `
 - Restricted to: `BOT_OWNER`

Set the maximum duration a timer can countdown.

## timerset showsettings
 - Usage: `[p]timerset showsettings `
 - Aliases: `ss`

Show current timer settings.