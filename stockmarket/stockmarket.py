import asyncio
import datetime
import noobutils as nu
import typing as t

from redbot.core import bank

from .objects import StockObject
from .utilities import is_economy_global
from .views import StockPaginatorView


DEFAULT_USER = {"owned_stocks": {}}
DEFAULT_GLOBAL = {"active": False, "stocks": {}}

"""
Config structure for stocks:

s = {
    "stock_name": {
        "bankrupt": False,
        "emoji": "emoji",
        "price": 69,
        "previous_price": 0,
        "percent": -0.24,
    }
}

Config structure for owned_stocks:

os = {
    "stock_name": 69
}
"""


class StockMarket(nu.Cog):
    """
    Stock Market Simulation Cog.

    Trade stocks on discord! This cog requires Red's core economy and it is set to Global Mode.
    """

    def __init__(self, bot: nu.Red, *args, **kwargs):
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.0.5",
            authors=["NoobInDaHause"],
            use_config=True,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.running = True
        self.initialized = asyncio.Event()
        self.config.register_global(**DEFAULT_GLOBAL)
        self.config.register_user(**DEFAULT_USER)
        self.price_changing_loop_task = bot.loop.create_task(self.price_changing_loop())
        self.save_stocks_loop_task = bot.loop.create_task(self.save_stocks_loop())
        self.next_date_run = datetime.datetime.now(datetime.timezone.utc)
        self.stocks: t.List[StockObject] = []

    async def red_delete_data_for_user(
        self,
        *,
        requester: t.Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog stores user ids for owned stocks purposes.

        Users can delete their data at any time.
        """
        await self.config.user_from_id(user_id).clear()

    async def to_config(self):
        new_stocks = {}
        for stock in self.stocks.copy():
            new_stocks |= stock.to_dict()

        await self.config.stocks.set(new_stocks)

    async def cog_load(self) -> None:
        self.bot.add_dev_env_value("stockmarket", lambda _: self)
        self.log.info("Price Changing Loop task started.")
        stocks: dict = await self.config.stocks()
        self.stocks.extend([StockObject(name=k, **v) for k, v in stocks.items()])

        self.initialized.set()

    async def cog_unload(self) -> None:
        self.running = False
        self.bot.remove_dev_env_value("stockmarket")
        self.price_changing_loop_task.cancel()
        self.save_stocks_loop_task.cancel()
        self.log.info("Price Changing Loop task cancelled.")
        if self.initialized.is_set():
            await self.to_config()

        self.initialized.clear()
        self.stocks.clear()

    async def price_changing_loop(self):
        await self.bot.wait_until_red_ready()
        await self.initialized.wait()

        while self.running:
            if await self.config.active():
                now = datetime.datetime.now(datetime.timezone.utc)
                self.next_date_run = now.replace(
                    second=0, microsecond=0
                ) + datetime.timedelta(
                    minutes=30 - (now.minute % 30)
                )  # every 30 minutes of real time e.g. XX:00 or XX:30

                await asyncio.sleep((self.next_date_run - now).total_seconds())

                if await bank.is_global():
                    for stock in self.stocks:
                        stock.update_price(self.next_date_run)

                    await self.to_config()
                else:
                    self.log.warning(
                        "Economy is not set to global! Please set it to global mode!"
                    )
            else:
                await asyncio.sleep(10)

    async def save_stocks_loop(self):
        await self.bot.wait_until_red_ready()
        await self.initialized.wait()

        while self.running:
            await asyncio.sleep(300)
            await self.to_config()
            self.log.debug("StockMarket config saved!")

    async def restart_price_changing_loop(self):
        self.price_changing_loop_task.cancel()
        self.price_changing_loop_task = None
        await asyncio.sleep(1)
        self.price_changing_loop_task = self.bot.loop.create_task(
            self.price_changing_loop()
        )

    @nu.commands.hybrid_group(name="stockmarket", aliases=["stockm"])
    @nu.commands.bot_has_permissions(embed_links=True)
    async def stockmarket(self, context: nu.commands.Context):
        """
        StockMarket base commands.

        If you can not see any sub-commands then that means Economy is not set to global!
        """
        pass

    @stockmarket.command(name="buy")
    @is_economy_global()
    async def stockmarket_buy(
        self, context: nu.commands.Context, stock_name: str, amount: int
    ):
        """
        Buy a stock from the StockMarket.
        """
        if (not await self.config.active()) and (
            not await self.bot.is_owner(context.author)
        ):
            return await context.send(
                content="The StockMarket is currently closed. Check back later.",
                ephemeral=True,
            )
        if not (stock := nu.discord.utils.get(self.stocks, name=stock_name)):
            return await context.send(content="That stock does not seem to exist.")
        if amount < 1:
            return await context.send(content="Invalid amount provided.")
        if stock.bankrupt:
            return await context.send(
                content="Unfortunately this stock is bankrupt and it is no longer worth buying it."
            )

        currency_name = await bank.get_currency_name()
        cost = stock.price * amount

        if cost > await bank.get_balance(context.author):
            return await context.send(
                content="You have insufficient funds to buy that many stocks."
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
            colour=self.bot._color,
            title="Confirmation",
            description=f"Are you sure you want to buy {human_amount} {stock.emoji} {stock}?",
        )
        embed.add_field(
            name="Total Cost:", value=f"{human_cost} {currency_name}", inline=False
        )
        embed.add_field(
            name="Cost per Stock:", value=f"{human_price} {currency_name}", inline=False
        )

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(embed=embed)
        await view.wait()

        if view.value:
            await bank.withdraw_credits(context.author, cost)

            async with self.config.user(context.author).owned_stocks() as os:
                owned_stocks: dict = os
                owned_stocks[stock.name] = owned_stocks.get(stock.name, 0) + amount

            await self.to_config()

    @stockmarket.command(name="sell")
    @is_economy_global()
    async def stockmarket_sell(
        self, context: nu.commands.Context, stock_name: str, amount: int
    ):
        """
        Sell a stock from the StockMarket.
        """
        if (not await self.config.active()) and (
            not await self.bot.is_owner(context.author)
        ):
            return await context.send(
                content="The StockMarket is currently closed. Check back later.",
                ephemeral=True,
            )
        if not (stock := nu.discord.utils.get(self.stocks, name=stock_name)):
            return await context.send(content="That stock does not seem to exist.")
        if amount < 1:
            return await context.send(content="Invalid amount provided.")

        currency_name = await bank.get_currency_name()
        async with self.config.user(context.author).owned_stocks() as os:
            owned_stocks: dict = os
            if (shares := owned_stocks.get(stock_name, 0)) < amount:
                return await context.send(
                    content=f"You have {nu.cf.humanize_number(shares)} {stock.emoji} {stock}. "
                    "You cannot sell that many stocks."
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
                colour=self.bot._color,
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

            view = nu.NoobConfirmation(obj=context, confirm_action=act)
            await view.start(embed=embed)
            await view.wait()

            if view.value:
                await bank.deposit_credits(context.author, revenue)
                (
                    owned_stocks.pop(stock_name)
                    if shares == amount
                    else owned_stocks.__setitem__(stock_name, shares - amount)
                )
                await self.to_config()

    @stockmarket.command(name="view")
    @is_economy_global()
    async def stockmarket_view(self, context: nu.commands.Context):
        """
        View the current stocks from the StockMarket.
        """
        if (not await self.config.active()) and (
            not await self.bot.is_owner(context.author)
        ):
            return await context.send(
                content="The StockMarket is currently closed. Check back later.",
                ephemeral=True,
            )
        if not self.stocks:
            return await context.send(content="It seems there are no stocks available.")

        currency_name = await bank.get_currency_name()
        owned_stocks: dict = await self.config.user(context.author).owned_stocks()
        list_embed = []
        stock_pages = {}

        async with context.typing():
            for stock in self.stocks.copy():
                page = len(list_embed) + 1
                owned = owned_stocks.get(stock.name, 0)
                last_updated = (
                    f"<t:{int(stock.last_updated.timestamp())}:f>"
                    if stock.last_updated
                    else "N/A"
                )
                e = nu.discord.Embed(
                    colour=self.bot._color,
                    title="StockMarket",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    description=(
                        f"- {stock.emoji} {stock}\n├ You currently own: {owned}"
                        f"\n├ Bankrupt: {stock.bankrupt}"
                        f"\n├ Current Price: {stock.price} {currency_name} **{stock.percent}** {stock.status}"
                        f"\n├ Previous Price: {stock.previous_price} {currency_name}"
                        f"\n├ Last Updated: {last_updated}"
                        f"\n└ Next Update: <t:{int(self.next_date_run.timestamp())}:R>\n\n```PRICE GRAPH:```"
                    ),
                )
                e.set_image(url=stock.graph_url)
                e.set_footer(
                    text=f"Page ({page}/{len(self.stocks)})",
                    icon_url=nu.is_have_avatar(context.guild),
                )
                e.set_author(
                    name=context.author.display_name,
                    icon_url=nu.is_have_avatar(context.author),
                )
                list_embed.append(e)
                stock_pages[str(page)] = stock.name

        await StockPaginatorView(
            obj=context.interaction or context,
            pages=list_embed,
            use_select_menu=True,
            use_page_button=False,
            stock_pages=stock_pages,
        ).start()

    @stockmarket.command(name="portfolio", aliases=["pf"])
    @is_economy_global()
    async def stockmarket_portfolio(self, context: nu.commands.Context):
        """
        View your StockMarket portfolio.
        """
        if (not await self.config.active()) and (
            not await self.bot.is_owner(context.author)
        ):
            return await context.send(
                content="The StockMarket is currently closed. Check back later.",
                ephemeral=True,
            )
        owned_stocks: dict = await self.config.user(context.author).owned_stocks()
        if not owned_stocks:
            return await context.send(content="You do not own any stocks.")

        currency_name = await bank.get_currency_name()
        embed = nu.discord.Embed(
            title=f"{context.author.display_name}'s owned stocks",
            colour=context.author.colour,
        )
        to_remove = []
        for stock, amount in owned_stocks.items():
            if st := nu.discord.utils.get(self.stocks, name=stock):
                msg = (
                    f"Amount: {nu.cf.humanize_number(amount)}\n"
                    f"Overall Price: {nu.cf.humanize_number(st.price * amount)} {currency_name}"
                )
                embed.add_field(name=f"{st.emoji} {st}", value=msg)
            else:
                to_remove.append(stock)

        if to_remove:
            for i in to_remove:
                owned_stocks.pop(i)
            await self.config.user(context.author).owned_stocks.set(owned_stocks)

        await context.send(embed=embed)

    @nu.commands.group(
        name="stockmarketset", aliases=["stockmset", "stockset", "smset"]
    )
    @nu.commands.bot_has_permissions(embed_links=True)
    @nu.commands.is_owner()
    @is_economy_global()
    async def stockmarketset(self, context: nu.commands.Context):
        """
        StockMarket settings commands.
        """
        pass

    @stockmarketset.command(name="activate")
    async def stockmarketset_activate(self, context: nu.commands.Context):
        """
        Activate or deactivate the StockMarket cog.
        """
        active = await self.config.active()
        await self.config.active.set(not active)
        await self.restart_price_changing_loop()
        await context.send(
            content=f"The StockMarket cog is now {'deactivated' if active else 'activated'}."
        )

    @stockmarketset.command(name="stock")
    async def stockmarketset_stock(
        self,
        context: nu.commands.Context,
        action: t.Literal["add", "remove", "edit"],
        stock_name: str,
        emoji: nu.NoobEmojiConverter = None,
        price: int = None,
        bankrupt: bool = None,
        new_name: str = None,
    ):
        """
        Add, Remove or Edit stocks.

        You can skip `new_name` argument if you are not editting a stock.
        You can skill all arguments if removing a stock.
        """
        if None in [emoji, price, bankrupt] and action == "add":
            return await context.send(
                content="All arguments are required for adding stocks except for `new_name`."
            )
        if action == "add":
            if nu.discord.utils.get(self.stocks, name=stock_name):
                return await context.send(content="That stock already exists")
            if len(self.stocks) >= 25:
                return await context.send(
                    content="You can only have a maximum of 25 stocks."
                )
            if price < 50:
                return await context.send(
                    content="The minimum price to add stock is 50. "
                    "Try setting it for more than or equal to 100 (recommended)."
                )

            self.stocks.append(
                StockObject(
                    name=stock_name,
                    price=price,
                    percent=0.0,
                    bankrupt=bankrupt,
                    emoji=str(emoji),
                    previous_price=0,
                )
            )
            await context.send(content="Successfully added that stock.")
        elif action == "edit":
            if not (stock := nu.discord.utils.get(self.stocks, name=stock_name)):
                return await context.send(content="That stock does not seem to exist.")
            if new_name:
                stock.name = new_name
            if emoji:
                stock.emoji = str(emoji)
            if price:
                stock.previous_price = stock.price
                stock.price = price
            if bankrupt is not None:
                stock.bankrupt = bankrupt
            await context.send(content="Successfully editted that stock.")
        else:
            if not (stock := nu.discord.utils.get(self.stocks, name=stock_name)):
                return await context.send(content="That stock does not seem to exist.")

            self.stocks.remove(stock)
            await context.send(content="Done, removed that stock.")

        await self.to_config()

    @stockmarketset.command(name="update")
    async def stockmarketset_update(self, context: nu.commands.Context):
        """
        Manually update the stock prices.

        I highly recommend you not to use this command since it is intended for debug and testing purposes.
        It is best that the stocks are updated every 30 minutes of real time but you do you I guess.
        """
        if not self.stocks:
            return await context.send(content="No stocks found.")

        for stock in self.stocks:
            stock.update_price(datetime.datetime.now(datetime.timezone.utc))

        await context.tick()

    @stockmarketset.command(name="resetcog")
    async def stockmarketset_resetcog(self, context: nu.commands.Context):
        """
        Reset the cog's data.
        """
        act = "Are you sure you want to wipe all of the StockMarket data?"
        conf = "Done wiped all those data."
        view = nu.NoobConfirmation(obj=context, confirm_action=conf)

        await view.start(content=act)
        await view.wait()

        if view.value:
            self.stocks.clear()
            await self.config.clear_all()
            await self.restart_price_changing_loop()

    @stockmarketset.command(name="showsettings", aliases=["ss"])
    async def stockmarketset_showsettings(self, context: nu.commands.Context):
        """
        View settings for StockMarket cog.
        """
        a = await self.config.active()
        p = self.price_changing_loop_task.done()
        s = self.save_stocks_loop_task.done()
        embed = nu.discord.Embed(
            colour=self.bot._color,
            title="StockMarket Settings",
            description=f"Activated: {a}\nStocks: {len(self.stocks)}\n"
            "Price Changing Loop Task Status: "
            f"{'❎ Task is not running! Reload the cog!' if p else '✅ Task is running as intended.'}\n"
            "Save Stocks Loop Task Status: "
            f"{'❎ Task is not running! Reload the cog!' if s else '✅ Task is running as intended.'}",
        )
        await context.send(embed=embed)
