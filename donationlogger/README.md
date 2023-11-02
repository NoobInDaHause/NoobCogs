# DonationLogger Help

Donation Logger System.<br/><br/>Log any donations from your server.

# donationlogger
 - Usage: `[p]donationlogger `
 - Aliases: `d, dl, dono, and donolog`
 - Checks: `guild_only`

DonationLogger base commands.

## donationlogger set
 - Usage: `[p]donationlogger set <bank_name> <amount> [member=None] `
 - Checks: `is_setup_done and is_a_dono_manager_or_higher`

Set someone's donation balance to the amount of your choice.

## donationlogger resetcog
 - Usage: `[p]donationlogger resetcog `
 - Restricted to: `BOT_OWNER`

Reset the cog's whole config.

## donationlogger setup
 - Usage: `[p]donationlogger setup `
 - Restricted to: `ADMIN`

Setup the donation logger system in this guild.

## donationlogger donationcheck
 - Usage: `[p]donationlogger donationcheck <bank_name> <mla> [amount=None] `
 - Aliases: `dc`
 - Checks: `is_setup_done`

See who has donated more or less or all from a bank.

## donationlogger resetmember
 - Usage: `[p]donationlogger resetmember [member=None] [bank_name=None] `
 - Checks: `is_setup_done and is_a_dono_manager_or_higher`

Reset a member's specific bank or all bank donations.

## donationlogger leaderboard
 - Usage: `[p]donationlogger leaderboard <bank_name> [top=10] `
 - Aliases: `lb`
 - Checks: `is_setup_done`

See who has donated the most from a bank.<br/><br/>Pass true in the all_donors argument to see all donators from a bank.

## donationlogger remove
 - Usage: `[p]donationlogger remove <bank_name> <amount> [member=None] `
 - Aliases: `- and r`
 - Checks: `is_setup_done and is_a_dono_manager_or_higher`

Remove bank donation amount to a member or yourself.

## donationlogger balance
 - Usage: `[p]donationlogger balance [member=None] [bank_name=None] `
 - Aliases: `bal, c, and check`
 - Checks: `is_setup_done`

Check your or some one else's donation balance.

## donationlogger add
 - Usage: `[p]donationlogger add <bank_name> <amount> [member=None] `
 - Aliases: `+ and a`
 - Checks: `is_setup_done and is_a_dono_manager_or_higher`

Add bank donation amount to a member or yourself.

# donationloggerset
 - Usage: `[p]donationloggerset `
 - Restricted to: `ADMIN`
 - Aliases: `dlset, donologset, and donoset`
 - Checks: `is_setup_done`

DonationLogger settings commands.

## donationloggerset manager
 - Usage: `[p]donationloggerset manager <add_remove_list> <roles> `

Add, Remove or check the list of managers.

## donationloggerset logchannel
 - Usage: `[p]donationloggerset logchannel [channel=None] `

Set or remove the log channel.

## donationloggerset showsettings
 - Usage: `[p]donationloggerset showsettings `
 - Aliases: `ss and showallsettings`

See all the current set settings for this guild's DonationLogger system.

## donationloggerset autorole
 - Usage: `[p]donationloggerset autorole `

Enable or Disable automatic role additon or removal.

## donationloggerset resetguild
 - Usage: `[p]donationloggerset resetguild `

Reset the guild's DonationLogger system.

## donationloggerset bank
 - Usage: `[p]donationloggerset bank `

Bank settings commands.

### donationloggerset bank resetbank
 - Usage: `[p]donationloggerset bank resetbank <roles_or_donators> <bank_name> `

Reset a banks donations or amountroles.

### donationloggerset bank amountroles
 - Usage: `[p]donationloggerset bank amountroles `
 - Aliases: `ar`

Bank Amount-Roles settings commands.

#### donationloggerset bank amountroles set
 - Usage: `[p]donationloggerset bank amountroles set <bank_name> <amountroles> `
 - Aliases: `add`

Set roles milestone to an amount.<br/><br/>Example: 10m:@role:@role,10k:(role_id),12.5e6:(role_name)<br/>You can only set a maximum of 3 roles per amount.

#### donationloggerset bank amountroles list
 - Usage: `[p]donationloggerset bank amountroles list <bank_name> `

See the list of amountroles on a bank.

#### donationloggerset bank amountroles remove
 - Usage: `[p]donationloggerset bank amountroles remove <bank_name> <amount> `

Remove an amount from the roles milestone.

### donationloggerset bank list
 - Usage: `[p]donationloggerset bank list `

See the list of registered banks.

### donationloggerset bank hidden
 - Usage: `[p]donationloggerset bank hidden <hidden> [bank_name=None] `

Hide, UnHide or see the list of hidden banks.

### donationloggerset bank remove
 - Usage: `[p]donationloggerset bank remove <bank_name> `

Remove a bank.

### donationloggerset bank add
 - Usage: `[p]donationloggerset bank add <bank_name> <emoji> [hidden=False] `

Add a new bank.

### donationloggerset bank emoji
 - Usage: `[p]donationloggerset bank emoji <bank_name> <emoji> `

Change a bank's emoji.

