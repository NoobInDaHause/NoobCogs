# ServerDonations Help

Donate bot currencies or any other currencies to servers.<br/><br/>Donate Nitro, Dank Memer Coins, Bro Coins, Owo Cash, Karuta Tickets and many more.

# giveawaydonate
 - Usage: `[p]giveawaydonate <giveaway> `
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `guild_only`

Donate to giveaways.<br/><br/>Split arguments with a vertical bar |.<br/>Put none in any of the optional [arguments] if you do not want anything on there.

# eventdonate
 - Usage: `[p]eventdonate <event> `
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `guild_only`

Donate to events.<br/><br/>Split arguments with a vertical bar |.<br/>Put none in any of the optional [arguments] if you do not want anything on there.

# heistdonate
 - Usage: `[p]heistdonate <heist> `
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `guild_only`

Donate to heists.<br/><br/>Split arguments with a vertical bar |.<br/>Put none in any of the optional [arguments] if you do not want anything on there.

# serverdonationsset
 - Usage: `[p]serverdonationsset `
 - Restricted to: `ADMIN`
 - Aliases: `sdonateset and sdonoset`
 - Checks: `guild_only`

Serverdonations settings.

## serverdonationsset autodelete
 - Usage: `[p]serverdonationsset autodelete `
 - Aliases: `autodel`

Toggle wheather to automatically delete command invocation.

## serverdonationsset resetcog
 - Usage: `[p]serverdonationsset resetcog `
 - Restricted to: `BOT_OWNER`

Reset the whole cog config.

## serverdonationsset message
 - Usage: `[p]serverdonationsset message <message_type> [message=None] `

Set the donation message.<br/><br/>Make sure you know TagScriptEngine.<br/>Available Blocks:<br/>If blocks, Random blocks, Fifty fifty blocks, Any blocks, All blocks, Embed blocks.<br/><br/>Available variables:<br/>{donor} - The donor.<br/>Ex: {donor(mention)}, {donor(name)}<br/>{server} - The server.<br/>Ex: {server(name)}, {server(id)}<br/>{role} - The manage role that gets mentioned.<br/> -  Events:<br/>{currency_type} - The type of currency that they want to donate.<br/>{event_name} - The event name.<br/>{requirements} - The requirements to join the event.<br/>{prize} - The prize of the event.<br/>{message} - The optional donor message.<br/> -  Giveaways:<br/>{currency_type} - The type of currency that they want to donate.<br/>{duration} - The duration of the giveaway.<br/>{winners} - The amount of winners for the giveaway.<br/>{requirements} - The requirements to join the giveaway.<br/>{prize} - The prize of the giveaway.<br/>{message} - The optional donor message.<br/> -  Heists:<br/>{currency_type} - The type of currency that they want to donate.<br/>{amount} - The amount of the heist.<br/>{requirements} - The requirements to join the heist.<br/>{message} - The optional donor message.

## serverdonationsset manager
 - Usage: `[p]serverdonationsset manager <manager_type> <action_type> <roles> `
 - Aliases: `managers`

Set the manager roles.<br/><br/>Leave role blank to reset role.

## serverdonationsset resetguild
 - Usage: `[p]serverdonationsset resetguild `

Reset your serverdonations guild settings.

## serverdonationsset showsettings
 - Usage: `[p]serverdonationsset showsettings `
 - Aliases: `ss`

See your current serverdonations guild settings.

## serverdonationsset channel
 - Usage: `[p]serverdonationsset channel <channel_type> [channel=None] `
 - Aliases: `chan and channels`

Set or remove the giveaway, event or heist donation channel.<br/><br/>Leave channel blank to remove the set one if there is one.