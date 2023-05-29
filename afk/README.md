# Afk Help

Notify users whenever you go AFK with pings logging.<br/><br/>Be afk and notify users who ping you with a reason of your choice. This cog is inspired by sravan and Andy's afk cog.

# afk (Hybrid Command)
 - Usage: `[p]afk [reason] `
 - Slash Usage: `/afk [reason] `
 - Aliases: `away`
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `guild_only`

Be afk and notify users whenever they ping you.<br/><br/>The reason is optional.

# afkset
 - Usage: `[p]afkset `
 - Aliases: `awayset`
 - Checks: `guild_only`

Settings for the AFK cog.

## afkset showsettings
 - Usage: `[p]afkset showsettings `
 - Aliases: `ss`

See your AFK settings.<br/><br/>Guild settings show up when you have manage_guild permission.

## afkset reset
 - Usage: `[p]afkset reset `

Reset your AFK settings to default.

## afkset members
 - Usage: `[p]afkset members `
 - Restricted to: `ADMIN`

Check who are all the afk members in your guild.

## afkset togglelogs
 - Usage: `[p]afkset togglelogs <state> `
 - Aliases: `tl`

Toggle whether to log all pings you recieved or not.

## afkset nick
 - Usage: `[p]afkset nick <state> `
 - Restricted to: `ADMIN`

Toggle whether to change the users nick with ***[AFK] {user_display_name}*** or not.<br/><br/>This defaults to True.

## afkset resetcog
 - Usage: `[p]afkset resetcog `
 - Restricted to: `BOT_OWNER`

Reset the AFK cogs configuration. (Bot owners only.)

## afkset sticky
 - Usage: `[p]afkset sticky <state> `

Toggle whether to sticky your afk or not.<br/><br/>This defaults to False.

## afkset forceafk
 - Usage: `[p]afkset forceafk <member> [reason] `
 - Restricted to: `ADMIN`
 - Aliases: `forceaway`

Forcefully add or remove an AFK status on a user.

## afkset deleteafter
 - Usage: `[p]afkset deleteafter <seconds> `
 - Restricted to: `ADMIN`
 - Aliases: `da`

Change the delete after on every AFK notify.<br/><br/>Leave seconds blank to disable.<br/>Default is 10 seconds.
