# Suggestion Help

Suggestion system.<br/><br/>Have users submit suggestions to help improve some things.

# suggest (Hybrid Command)
 - Usage: `[p]suggest <suggestion> `
 - Slash Usage: `/suggest <suggestion> `
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `guild_only`

Suggest stuff.

# approve
 - Usage: `[p]approve <suggestion_id> [reason] `
 - Restricted to: `ADMIN`
 - Checks: `guild_only`

Approve a suggestion.

# reject
 - Usage: `[p]reject <suggestion_id> [reason] `
 - Restricted to: `ADMIN`
 - Checks: `guild_only`

Reject a suggestion.

# suggestionset
 - Usage: `[p]suggestionset `
 - Restricted to: `ADMIN`
 - Aliases: `suggestset`
 - Checks: `guild_only`

Configure the suggestion cog.

## suggestionset editreason
 - Usage: `[p]suggestionset editreason <suggestion_id> <reason> `

Edit a suggestions reason.

## suggestionset emoji
 - Usage: `[p]suggestionset emoji <vote> <emoji> `

Change the UpVote or DownVote emoji.

## suggestionset showsettings
 - Usage: `[p]suggestionset showsettings `
 - Aliases: `ss`

Show the current suggestion cogs guild settings.

## suggestionset view
 - Usage: `[p]suggestionset view <suggestion_id> `

View a suggestion.

## suggestionset resetcog
 - Usage: `[p]suggestionset resetcog `
 - Restricted to: `BOT_OWNER`

Reset the whole cogs configuration.

## suggestionset autodelete
 - Usage: `[p]suggestionset autodelete `
 - Aliases: `autodel`

Toggle whether to automatically delete suggestion commands or not.

## suggestionset channel
 - Usage: `[p]suggestionset channel <type> <channel> `
 - Aliases: `chan`

Set the suggestion channel.<br/><br/>Leave channel blank to remove the current set channel on what type you used.

## suggestionset buttoncolor
 - Usage: `[p]suggestionset buttoncolor <types> <colour> `
 - Aliases: `buttoncolour`

Change the upvote or downvotes button colour.<br/><br/>Leave colour blank to reset the colour of the type you put.<br/><br/>Available colours:<br/>- red<br/>- green<br/>- blurple<br/>- grey

## suggestionset reset
 - Usage: `[p]suggestionset reset `

Reset the guilds settings to default.