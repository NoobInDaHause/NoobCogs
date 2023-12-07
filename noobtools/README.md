# NoobTools Help

NoobInDahause's personal tools.

# amarilevel (Hybrid Command)
 - Usage: `[p]amarilevel [member=None] `
 - Slash Usage: `/amarilevel [member=None] `
 - Aliases: `alvl, alevel, and amari`
 - Cooldown: `1 per 5.0 seconds`
 - Checks: `guild_only`

Check your or someone else's amari level.<br/><br/>Requires amari api token.<br/>If you are the bot owner apply for one in their support server [here](https://discord.gg/kqefESMzQj).<br/>If you already have an amari api token set it with:<br/>[p]set api amari auth,<your_api_key>

# reach
 - Usage: `[p]reach <channel> <roles> `
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `guild_only`

Reach channel and see how many members who can view the channel.<br/><br/>Separate roles with a space if multiple. (ID's accepted)<br/>Role searching may or may not be 100% accurate.<br/>You can pass everyone or here to check @everyone or @here reach.

# membercount (Hybrid Command)
 - Usage: `[p]membercount `
 - Slash Usage: `/membercount `
 - Aliases: `mcount`

See the total members in this guild.

# randomcolour
 - Usage: `[p]randomcolour `
 - Aliases: `randomcolor`

Generate a random colour.

# changetickemoji
 - Usage: `[p]changetickemoji [emoji=None] `
 - Restricted to: `BOT_OWNER`

Change [botname]'s tick emoji.<br/><br/>Leave emoji parameter as blank to check current tick emoji.

# changeauditreason
 - Usage: `[p]changeauditreason <check> `
 - Restricted to: `BOT_OWNER`

This command changes [botname]'s audit reason.<br/><br/>For every cog that uses audit reasons.<br/><br/>Add check to see current settings or reset to reset settings.<br/><br/>Available variables:<br/>{author_name}: The audit authors name.<br/>{author_id}: The audit authors ID.<br/>{reason}: The audit reason.<br/><br/>Note:<br/>You need all three variables present in the audit that is with reason.