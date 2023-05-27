# ServerDonations Help

Donate bot currencies or other things to guilds.<br/><br/>Base commands to donate to guild giveaways, events, heists etc.

# sdonatehelp
 - Usage: `[p]sdonatehelp `

Know how to run the donation commands.<br/><br/>Available commands:<br/>[p]giveawaydonate<br/>[p]eventdonate<br/>[p]heistdonate

# serverdonationsset
 - Usage: `[p]serverdonationsset `
 - Restricted to: `ADMIN`
 - Aliases: `sdonateset and sdonoset`

Configure the ServerDonations configuration settings.

## serverdonationsset reset
 - Usage: `[p]serverdonationsset reset `

Reset the serverdonations guild settings to default.

## serverdonationsset resetcog
 - Usage: `[p]serverdonationsset resetcog `
 - Restricted to: `BOT_OWNER`

Reset the ServerDonations cogs configuration.<br/><br/>Bot owners only.

## serverdonationsset embed
 - Usage: `[p]serverdonationsset embed `

Customize the giveaway, event or heist donation request embed.

### serverdonationsset embed title
 - Usage: `[p]serverdonationsset embed title <type> <title> `

Customize the title for giveaway, event or heist donation embed.<br/><br/>Leave title blank to reset it to default for the given type<br/><br/>Available variables:<br/> -  {guild.name} - The guilds name.<br/> -  {guild.id} - The guilds ID.<br/> -  {donor} - The donors username.<br/> -  {donor.id} - The donors ID.

### serverdonationsset embed content
 - Usage: `[p]serverdonationsset embed content <type> <content> `

Customize the content for giveaway, event or heist donation embed.<br/><br/>Leave content blank to reset it to default for the given type.<br/><br/>Available variables:<br/> -  {role} - The ping role.<br/> -  {guild.name} - The guilds name.<br/> -  {guild.id} - The guilds ID.<br/> -  {donor} - The donors username.<br/> -  {donor.id} - The donors ID.<br/> -  {donor.mention} - Mentions the donor.

### serverdonationsset embed thumbnail
 - Usage: `[p]serverdonationsset embed thumbnail <type> <url_or_avatar> `

Customize the thumbnail for giveaway, event or heist donation embed.<br/><br/>Leave url_or_avatar blank to remove the thumbnail<br/><br/>Put 'reset' in url_or_avatar to reset it to default.<br/><br/>Available variables:<br/> -  {guild} - The guilds icon.<br/> -  {donor} - The donors avatar.<br/> -  Any valid url or link.<br/><br/>Note:<br/>If you use any one of the variables please put it exactly the same as the above and only that.

### serverdonationsset embed field
 - Usage: `[p]serverdonationsset embed field <type> `
 - Aliases: `fields`

Customize the fields for the giveaway, event or heist donation embed.

### serverdonationsset embed image
 - Usage: `[p]serverdonationsset embed image <type> <url> `

Customize the image for the giveaway, event or heist donation embed.<br/><br/>Leave url blank to remove the image.<br/><br/>Put 'reset' in url to reset it to default.

### serverdonationsset embed footer
 - Usage: `[p]serverdonationsset embed footer <type> <type2> [url_or_text=None] `

Customize the footer for the giveaway, event or heist embed.<br/><br/>Leave url_or_text blank to remove the icon or text.<br/><br/>Put 'reset' in url_or_text to reset the icon if icon or text if text.<br/><br/>Available variables for the icon:<br/> -  {guild_icon} - The guilds icon.<br/> -  {donor_avatar} - The donors avatar.<br/> -  Any valid urls.<br/><br/>Note:<br/>If you use any one of the variables please put it exactly the same as the above and only that.

### serverdonationsset embed description
 - Usage: `[p]serverdonationsset embed description <type> <description> `

Customize the description for giveaway, event or heist donation embed.<br/><br/>Leave description blank to reset it to default.<br/><br/>Available variables:<br/> -  {guild.name} - The guilds name.<br/> -  {guild.id} - The guilds ID.<br/> -  {donor} - The donors username.<br/> -  {donor.id} - The donors ID.<br/> -  {donor.mention} - Mentions the donor.

### serverdonationsset embed colour
 - Usage: `[p]serverdonationsset embed colour <type> <colour> `
 - Aliases: `color`

Customize the colour for giveaway, event or heist donation embed.<br/><br/>Leave colour blank to reset it to default.<br/><br/>All the colours defaults to bots embed colour.

## serverdonationsset showsettings
 - Usage: `[p]serverdonationsset showsettings `
 - Aliases: `ss`

See the guild settings set for ServerDonations.

## serverdonationsset role
 - Usage: `[p]serverdonationsset role <type> <role> `

Set the giveaway, event or heist manager role.<br/><br/>Leave role blank to remove the current set role for the given type.

## serverdonationsset channel
 - Usage: `[p]serverdonationsset channel <type> <channel> `
 - Aliases: `chan`

Set the giveaway, event or heist donation request channel.<br/><br/>Leave channel blank to remove the current set channel for the given type.

# giveawaydonate
 - Usage: `[p]giveawaydonate <type> | <duration> | <winners> | [requirements] | <prize> | [message] `
 - Aliases: `gdonate and gdono`
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `server_only`

Donate to guild giveaways.<br/><br/>Split arguments with |.<br/>See [p]sdonatehelp to know how to donate.

# eventdonate
 - Usage: `[p]eventdonate <type> | <name> | [requirements] | <prize> | [message] `
 - Aliases: `edonate and edono`
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `server_only`

Donate to guild events.<br/><br/>Split arguments with |.<br/>See [p]sdonatehelp to know how to donate.

# heistdonate
 - Usage: `[p]heistdonate <type> | <amount> | [requirements] | [message] `
 - Aliases: `hdonate and hdono`
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `server_only`

Donate to guild heists.<br/><br/>Split arguments with |.<br/>This command is especially designed for Bro bot and/or Dank Memer Bot or any other bot that has the similar feature.<br/>See [p]sdonatehelp to know how to donate.
