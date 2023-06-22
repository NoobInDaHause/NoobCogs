# JoinDM Help

DM newly joined users from your guild with your set message.<br/><br/>This cog uses TagScriptEngine and requires you basic tagscript knowledge to use this cog.

# joindmset
 - Usage: `[p]joindmset `
 - Restricted to: `ADMIN`
 - Aliases: `jdmset`

Configure your joindm settings.

## joindmset resetcog
 - Usage: `[p]joindmset resetcog `
 - Restricted to: `BOT_OWNER`

Reset the cogs whole configuration.

## joindmset toggle
 - Usage: `[p]joindmset toggle `

Toggle the joindm on or off.

## joindmset showsettings
 - Usage: `[p]joindmset showsettings `
 - Aliases: `ss`

Show the currently joindm guild settings.

## joindmset reset
 - Usage: `[p]joindmset reset `

Reset your current joindm guild settings.

## joindmset message
 - Usage: `[p]joindmset message <message> `
 - Aliases: `msg`

Set the join dm message.<br/><br/>Leave message blank to clear message.<br/><br/>Available variables:<br/>{member} - Member block.<br/>{guild} - Guild block.<br/><br/>Example:<br/> -  Hello {member(mention)} ({member(id)})! Welcome to {guild} ({guild(id)})!