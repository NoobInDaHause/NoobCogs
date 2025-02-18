from __future__ import annotations

import noobutils as nu
import typing as t

from redbot.core import bank

if t.TYPE_CHECKING:
    from . import StockMarket


class BuyOrSellModal(nu.discord.ui.Modal):
    def __init__(
        self,
        title: str,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(title=title, timeout=timeout)

    amount = nu.discord.ui.TextInput(min_length=1, label="Input amount.")

    async def on_submit(self, interaction: nu.discord.Interaction):
        await interaction.response.defer()

    async def on_error(self, interaction: nu.discord.Interaction, error: Exception):
        await interaction.response.send_message(
            content=f"Something went wrong. Please report this to the bot owner.\n{nu.cf.box(str(error))}",
            ephemeral=True,
        )


class StockPaginatorView(nu.NoobPaginator):
    def __init__(
        self,
        *,
        obj: t.Union[nu.discord.Interaction[nu.Red, nu.commands.Context]],
        pages: t.List[t.Union[str, nu.discord.Embed]],
        use_select_menu: bool = False,
        use_page_button: bool = True,
        access_denied_as_video: bool = True,
        is_ephemeral: bool = False,
        timeout: float = 180,
        stock_pages: dict = None,
    ):
        super().__init__(
            obj=obj,
            pages=pages,
            use_select_menu=use_select_menu,
            use_page_button=use_page_button,
            access_denied_as_video=access_denied_as_video,
            is_ephemeral=is_ephemeral,
            timeout=timeout,
        )
        self.stock_pages = stock_pages if stock_pages is not None else {}

    @nu.discord.ui.button(label="Buy")
    async def buy_button(
        self,
        interaction: nu.discord.Interaction[nu.Red],
        button: nu.discord.ui.Button[StockPaginatorView],
    ):
        stock_name = self.stock_pages[str(self.current_page + 1)]
        cog: "StockMarket" = interaction.client.get_cog("StockMarket")

        if (not await cog.config.active()) and (
            not await interaction.client.is_owner(interaction.user)
        ):
            return await interaction.response.send_message(
                content="The StockMarket is currently closed. Check back later.",
                ephemeral=True,
            )
        if not (stock := nu.discord.utils.get(cog.stocks, name=stock_name)):
            return await interaction.response.send_message(
                content="That stock does not seem to exist.", ephemeral=True
            )
        if stock.bankrupt:
            return await interaction.response.send_message(
                content="Unfortunately this stock is bankrupt and it is no longer worth buying it.",
                ephemeral=True
            )

        modal = BuyOrSellModal(f"How many {stock_name} would you like to buy?")
        await interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.amount.value:
            return
        try:
            amount = int(modal.amount.value)
            if amount < 1:
                return await interaction.followup.send(
                    content="Invalid amount provided.", ephemeral=True
                )
        except ValueError:
            return await interaction.followup.send(
                content=f"Invalid amount provided.",
                ephemeral=True,
            )

        currency_name = await bank.get_currency_name()
        cost = stock.price * amount
        if cost > await bank.get_balance(interaction.user):
            return await interaction.followup.send(
                content="You have insufficient funds to buy that many stock.",
                ephemeral=True,
            )

        human_amount = nu.cf.humanize_number(amount)
        human_cost = nu.cf.humanize_number(cost)
        human_price = nu.cf.humanize_number(stock.price)

        plural = "shares" if amount > 1 else "share"
        act = (
            f"Bought {human_amount} {plural} of {stock.emoji} {stock}.\n"
            f"**Total Cost:** {human_cost} {currency_name}\n**Cost per Stock:** {human_price} {currency_name}"
        )

        embed = nu.discord.Embed(
            colour=interaction.client._color,
            title="Confirmation",
            description=f"Are you sure you want to buy {human_amount} {stock.emoji} {stock}?",
        )
        embed.add_field(
            name="Total Cost:", value=f"{human_cost} {currency_name}", inline=False
        )
        embed.add_field(
            name="Cost per Stock:", value=f"{human_price} {currency_name}", inline=False
        )

        view = nu.NoobConfirmation(obj=interaction, confirm_action=act)
        await view.start(embed=embed)
        await view.wait()

        if view.value:
            await bank.withdraw_credits(interaction.user, cost)

            async with cog.config.user(interaction.user).owned_stocks() as os:
                owned_stocks: dict = os
                owned_stocks[stock.name] = owned_stocks.get(stock.name, 0) + amount

            await cog.to_config()

    @nu.discord.ui.button(label="Sell")
    async def sell_button(
        self,
        interaction: nu.discord.Interaction[nu.Red],
        button: nu.discord.ui.Button[StockPaginatorView],
    ):
        stock_name = self.stock_pages[str(self.current_page + 1)]
        cog: "StockMarket" = interaction.client.get_cog("StockMarket")

        if (not await cog.config.active()) and (
            not await interaction.client.is_owner(interaction.user)
        ):
            return await interaction.response.send_message(
                content="The StockMarket is currently closed. Check back later.",
                ephemeral=True,
            )
        if not (stock := nu.discord.utils.get(cog.stocks, name=stock_name)):
            return await interaction.response.send_message(
                content="That stock does not seem to exist.", ephemeral=True
            )

        modal = BuyOrSellModal(f"How many {stock_name} would you like to sell?")
        await interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.amount.value:
            return
        try:
            amount = int(modal.amount.value)
            if amount < 1:
                return await interaction.followup.send(
                    content="Invalid amount provided.", ephemeral=True
                )
        except ValueError:
            return await interaction.followup.send(
                content="Invalid amount provided.",
                ephemeral=True,
            )

        currency_name = await bank.get_currency_name()
        async with cog.config.user(interaction.user).owned_stocks() as os:
            owned_stocks: dict = os
            if (shares := owned_stocks.get(stock_name, 0)) < amount:
                return await interaction.followup.send(
                    content=f"You have {nu.cf.humanize_number(shares)} {stock.emoji} {stock}. "
                    "You cannot sell that many stocks.",
                    ephemeral=True,
                )

            revenue = stock.price * amount
            human_amount = nu.cf.humanize_number(amount)
            human_revenue = nu.cf.humanize_number(revenue)
            human_price = nu.cf.humanize_number(stock.price)

            plural = "shares" if amount > 1 else "share"
            act = (
                f"Sold {human_amount} {plural} of {stock.emoji} {stock}.\n"
                f"**Total Revenue:** {human_revenue} {currency_name}\n"
                f"**Cost per Stock:** {human_price} {currency_name}"
            )

            embed = nu.discord.Embed(
                colour=interaction.client._color,
                title="Confirmation",
                description=f"Are you sure you want to sell {human_amount} {stock.emoji} {stock}?",
            )
            embed.add_field(
                name="Total Revenue:",
                value=f"{human_revenue} {currency_name}",
                inline=False,
            )
            embed.add_field(
                name="Cost per Stock:",
                value=f"{human_price} {currency_name}",
                inline=False,
            )

            view = nu.NoobConfirmation(obj=interaction, confirm_action=act)
            await view.start(embed=embed)
            await view.wait()

            if view.value:
                await bank.deposit_credits(interaction.user, revenue)
                (
                    owned_stocks.pop(stock_name)
                    if shares == amount
                    else owned_stocks.__setitem__(stock_name, shares - amount)
                )
                await cog.to_config()
