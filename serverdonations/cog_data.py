from redbot.core.utils.chat_formatting import box

class SdonateDefaults:
    """
    Cog config data.
    """
    default_guild = {
        "roles": {
            "gman": None,
            "eman": None,
            "hman": None
        },
        "channels": {
            "gchan": None,
            "echan": None,
            "hchan": None
        },
        "embeds": {
            "giveaway": {
                "g_content": "{role}",
                "g_title": "Someone would like to donate for a giveaway!",
                "g_desc": None,
                "g_colour": None,
                "g_thumb": "{donor_avatar}",
                "g_image": None,
                "g_footer": {
                    "g_ftext": "{guild.name}",
                    "g_ficon": "{guild_icon}"
                },
                "g_fields": {
                    "g_type": {
                        "g_tname": "**Type:**",
                        "g_tvalue": "{type}",
                        "g_tinline": False
                    },
                    "g_spon": {
                        "g_sname": "**Sponsor:**",
                        "g_svalue": "{sponsor}",
                        "g_sinline": True
                    },
                    "g_dura": {
                        "g_dname": "**Duration:**",
                        "g_dvalue": "{diration}",
                        "g_dinline": True
                    },
                    "g_winn": {
                        "g_wname": "**Winners:**",
                        "g_wvalue": "{winners}",
                        "g_winline": False
                    },
                    "g_requ": {
                        "g_rname": "**Requirements:**",
                        "g_rvalue": "{requirements}",
                        "g_rinline": True
                    },
                    "g_priz": {
                        "g_pname": "**Prize:**",
                        "g_pvalue": "{prize}",
                        "g_pinline": True
                    },
                    "g_mess": {
                        "g_mname": "**Message:**",
                        "g_mvalue": "{message}",
                        "g_minline": False
                    }
                }
            },
            "event": {
                "e_content": "{role}",
                "e_title": "Someone would like to donate for an event!",
                "e_desc": None,
                "e_colour": None,
                "e_thumb": "{donor_avatar}",
                "e_image": None,
                "e_footer": {
                    "e_ftext": "{guild.name}",
                    "e_ficon": "{guild_icon}"
                },
                "e_fields": {
                    "e_spon": {
                        "e_sname": "**Sponsor:**",
                        "e_svalue": "{sponsor}",
                        "e_sinline": False
                    },
                    "e_name": {
                        "e_nname": "**Name:**",
                        "e_nvalue": "{name}",
                        "e_ninline": False
                    },
                    "e_requ": {
                        "e_rname": "**Requirements:**",
                        "e_rvalue": "{requirements}",
                        "e_rinline": False
                    },
                    "e_priz": {
                        "e_pname": "**Prize:**",
                        "e_pvalue": "{prize}",
                        "e_pinline": False
                    },
                    "e_mess": {
                        "e_mname": "**Message:**",
                        "e_mvalue": "{message}",
                        "e_minline": False
                    },
                    "e_type": {
                        "e_tname": "**Type:**",
                        "e_tvalue": "{type}",
                        "e_tinline": False
                    }
                }
            },
            "heist": {
                "h_content": "{role}",
                "h_title": "Someone would like to donate for a heist!",
                "h_desc": None,
                "h_colour": None,
                "h_thumb": "{donor_avatar}",
                "h_image": None,
                "h_footer": {
                    "h_ftext": "{guild.name}",
                    "h_ficon": "{guild_icon}"
                },
                "h_fields": {
                    "h_type": {
                        "h_tname": "**Type:**",
                        "h_tvalue": "{type}",
                        "h_tinline": False
                    },
                    "h_spon": {
                        "h_sname": "**Sponsor:**",
                        "h_svalue": "{sponsor}",
                        "h_sinline": False
                    },
                    "h_amou": {
                        "h_aname": "**Amount:**",
                        "h_avalue": "{amount}",
                        "h_ainline": False
                    },
                    "h_requ": {
                        "h_rname": "**Requirements:**",
                        "h_rvalue": "{requirements}",
                        "h_rinline": False
                    },
                    "h_mess": {
                        "h_mname": "**Message:**",
                        "h_mvalue": "{message}",
                        "h_minline": False
                    }
                }
            }
        }
    }

class SdonateDesc:
    """
    Long ass descriptions.
    """
    gcmd = "Syntax: [p]giveawaydonate <type> | <duration> | <winners> | [requirements] | <prize> | [message]\nAlias: [p]gdonate, [p]gdono"
    gdonodesc = f"""
        {box(gcmd, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        **Duration**
        ` - ` The duration is how long would the giveaway last.
        **Winners**
        ` - ` The amount of winners for the giveaway.
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `none` if you do not want any requirements.
        **Prize**
        ` - ` The prize of the giveaway.
        **Message**
        ` - ` Send an optional message to the giveaway.
        ` - ` Type `none` if you do not want to send a message.
        
        Notes:
            You must split arguments with `|`.
            Arguments surrounded by [] are optional put `none` if you do not want to put anything.
        
        Example:
            `[p]giveawaydonate Dank Memer | 1 day and 12 hours | 1 winner | none | 69 coins | hallo guys welcome to my minecraft channel.`
        """

    ecmd = "Syntax: [p]eventdonate <type> | <event> | [requirements] | <prize> | [message]\nAlias: [p]]edonate, [p]edono"
    edonodesc = f"""
        {box(ecmd, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        **Event**
        ` - ` The type of event that you want to sponsor. (this can be any event or games that users can play)
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `none` if you do not want any requirements.
        **Prize**
        ` - ` The prize of the event.
        **Message**
        ` - ` Send an optional message to the event.
        ` - ` Type `none` if you do not want to send a message.
        
        Notes:
            You must split arguments with `|`.
            Arguments surrounded by [] are optional put `none` if you do not want to put anything.
        
        Example:
            `[p]eventdonate Owo bot | Split Or Steal | none | 1m owo coins | can i have chezburger plz`
        """

    hcmd = "Syntax: [p]heistdonate <type> | [requirements] | <amount> | [message]\nAlias: [p]hdonate, [p]hdono"
    hdonodesc = f"""
        {box(hcmd, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `none` if you do not want any requirements.
        **Amount**
        ` - ` The amount that you want to donate.
        **Message**
        ` - ` Send an optional message to the event.
        ` - ` Type `none` if you do not want to send a message.
        
        Notes:
            You must split arguments with `|`.
            Arguments surrounded by [] are optional put `none` if you do not want to put anything.

        Examples:
            `[p]heistdonate Bro Bot | none | 69420 coins | heist this baby up`
        """

class SDEmbedData:
    """
    Embed data.
    """
    gaw = """
    **Embed Content:**
    ```{s1}```
    **Embed Title:**
    ```{s2}```
    **Embed Description:**
    ```{s3}```
    **Embed Colour:**
    ```{s4}```
    **Embed Thumbnail:**
    ```{s5}```
    **Embed Image:**
    ```{s6}```
    **Embed Footer:**
    ```Text: {s7}
Icon: {s8}```
    **Embed Type Field:**
    ```Name: {s9}
Value: {s10}
Inline: {s11}```
    **Embed Sponsor Field:**
    ```Name: {s12}
Value: {s13}
Inline: {s14}```
    **Embed Duration Field:**
    ```Name: {s15}
Value: {s16}
Inline: {s17}```
    **Embed Winners Field:**
    ```Name: {s18}
Value: {s19}
Inline: {s20}```
    **Embed Requirements Field:**
    ```Name: {s21}
Value: {s22}
Inline: {s23}```
    **Embed Prize Field:**
    ```Name: {s24}
Value: {s25}
Inline: {s26}```
    **Embed Message Field:**
    ```Name: {s27}
Value: {s28}
Inline: {s29}```
    """

    event = """
    **Embed Content:**
    ```{s1}```
    **Embed Title:**
    ```{s2}```
    **Embed Description:**
    ```{s3}```
    **Embed Colour:**
    ```{s4}```
    **Embed Thumbnail:**
    ```{s5}```
    **Embed Image:**
    ```{s6}```
    **Embed Footer:**
    ```Text: {s7}
Icon: {s8}```
    **Embed Type Field:**
    ```Name: {s24}
Value: {s25}
Inline: {s26}```
    **Embed Sponsor Field:**
    ```Name: {s9}
Value: {s10}
Inline: {s11}```
    **Embed Name Field:**
    ```Name: {s12}
Value: {s13}
Inline: {s14}```
    **Embed Requirements Field:**
    ```Name: {s15}
Value: {s16}
Inline: {s17}```
    **Embed Prize Field:**
    ```Name: {s18}
Value: {s19}
Inline: {s20}```
    **Embed Message Field:**
    ```Name: {s21}
Value: {s22}
Inline: {s23}```
    """

    heist = """
    **Embed Content:**
    ```{s1}```
    **Embed Title:**
    ```{s2}```
    **Embed Description:**
    ```{s3}```
    **Embed Colour:**
    ```{s4}```
    **Embed Thumbnail:**
    ```{s5}```
    **Embed Image:**
    ```{s6}```
    **Embed Footer:**
    ```Text: {s7}
Icon: {s8}```
    **Embed Type Field:**
    ```Name: {s9}
Value: {s10}
Inline: {s11}```
    **Embed Sponsor Field:**
    ```Name: {s12}
Value: {s13}
Inline: {s14}```
    **Embed Amount Field:**
    ```Name: {s15}
Value: {s16}
Inline: {s17}```
    **Embed Requirements Field:**
    ```Name: {s18}
Value: {s19}
Inline: {s20}```
    **Embed Message Field:**
    ```Name: {s21}
Value: {s22}
Inline: {s23}```
    """