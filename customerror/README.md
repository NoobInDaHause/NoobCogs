# CustomError Help

Customize your bots error message.<br/><br/>Red already has a core command that changes the error message but I made my own with customization.<br/>This cog uses TagScriptEngine so be sure you have knowledge in that.<br/>Credits to sitryk, cray and phen for some of the code.

# customerror
 - Usage: `[p]customerror `
 - Restricted to: `BOT_OWNER`

Base commands for customizing the bots error message.<br/><br/>Bot owners only.

## customerror reset
 - Usage: `[p]customerror reset `

Reset the cogs settings.<br/><br/>Bot owners only.

## customerror plzerror
 - Usage: `[p]customerror plzerror `

Test the bots error message.<br/><br/>Bot owners only.

## customerror message
 - Usage: `[p]customerror message <message> `

Customize [botname]'s error message. (Bot owners only)<br/><br/>Bot owners only.<br/>Be sure that you have TagScriptEgnine knowledge.<br/>Available variables:<br/>{author} - The command invoker.<br/>{author(id)} - The command invokers ID.<br/>{author(mention)} - Mention the command invoker.<br/>{guild} - The guild.<br/>{guild(id)} - The guilds ID.<br/>{channel} - The channel.<br/>{channel(id)} - The channel ID.<br/>{channel(mention)} - Mention the channel.<br/>{error} - The raised command error.<br/>{command} - The command name.<br/>{message_content} - The message content.<br/>{message_id} - The message ID.<br/>{message_jump_url} - The message jump url.

## customerror showsettings
 - Usage: `[p]customerror showsettings `
 - Aliases: `ss`

See your current settings for the CustomError cog.<br/><br/>Bot owners only.