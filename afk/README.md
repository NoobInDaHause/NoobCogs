# Welcome to the AFK Cogs help README.

Be afk and notify users who ping you with a reason of your choice. This cog is inspired by sravan and Andy's afk cog.

## [Hybrid Commands] 
Below are Hybrid Commands can be run with legacy prefix commands or slash commands.

`[p]` is your bots prefix.

Words that are surrounded by `[]` are optional arguments while `<>` is rquired.

# [p]afk
 - `Usage:` [p]afk [reason]
 - `Aliases:` [p]away
 - `User permission(s):` None
 - `Bot permission(s):` embed_links, manage_nicknames
 - `Checks:` guild_only
 - `Description:` Be afk and notify users whenever they ping you.

## [Hybrid Group]
Below are Hybrid Group Commands can be run with legacy prefix commands or slash commands.

`[p]` is your bots prefix.

Words that are surrounded by `[]` are optional arguments while `<>` is rquired.

# [p]afkset
 - `Usage:` [p]afkset <sub_command>
 - `Aliases:` [p]awayset
 - `User permission(s):` None
 - `Bot permission(s):` embed_links
 - `Checks:` guild_only
 - `Description:` Settings for the AFK cog.

# [p]afkset deleteafter
 - `Usage:` [p]afkset deleteafter [seconds]
 - `Aliases:` [p]afkset da
 - `User permission(s):` Bot Owner
 - `Bot permission(s):` None
 - `Checks:` guild_only
 - `Description:` Change the delete after on every AFK notify.

# [p]afkset forceafk
 - `Usage:` [p]afkset forceafk <member> [reason]
 - `Aliases:` [p]afkset forceaway
 - `User permission(s):` manage_guild
 - `Bot permission(s):` embed_links
 - `Checks:` guild_only
 - `Description:` Forcefully add or remove an AFK status on a user.

# [p]afkset nick
 - `Usage:` [p]afkset nick <state>
 - `Aliases:` None
 - `User permission(s):` manage_guild
 - `Bot permission(s):` manage_nicknames
 - `Checks:` guild_only
 - `Description:` Toggle whether to change the users nick with `[AFK] {user.display_name}` or not.

# [p]afkset reset
 - `Usage:` [p]afkset reset
 - `Aliases:` None
 - `User permission(s):` None
 - `Bot permission(s):` None
 - `Checks:` guild_only
 - `Description:` Reset your AFK settings to default.

# [p]afkset resetcog
 - `Usage:` [p]afkset resetcog
 - `Aliases:` None
 - `User permission(s):` Bot Owner
 - `Bot permission(s):` None
 - `Checks:` Any
 - `Description:` Reset the AFK cogs configuration.

# [p]afkset showsetting
 - `Usage:` [p]afkset showsetting
 - `Aliases:` [p]afkset showsettings, [p]afkset showset, [p]afkset ss
 - `User permission(s):` None
 - `Bot permission(s):` None
 - `Checks:` guild_only
 - `Description:` See your AFK settings and Guild settings (if manage_guild+).

# [p]afkset sticky
 - `Usage:` [p]afkset sticky <state>
 - `Aliases:` None
 - `User permission(s):` None
 - `Bot permission(s):` None
 - `Checks:` guild_only
 - `Description:` Toggle whether to sticky your afk or not.

# [p]afkset togglelogs
 - `Usage:` [p]afkset togglelogs <state>
 - `Aliases:` [p]afkset tl
 - `User permission(s):` None
 - `Bot permission(s):` None
 - `Checks:` guild_only
 - `Description:` Toggle whether to log all pings you recieved or not.
