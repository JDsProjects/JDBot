import discord
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter
from jishaku.cog import OPTIONAL_FEATURES, STANDARD_FEATURES
from jishaku.exception_handling import ReplResponseReactor
from jishaku.features.baseclass import Feature
from jishaku.functools import AsyncSender
from jishaku.repl import AsyncCodeExecutor, get_var_dict_from_ctx

# look into making more jishaku commands: https://jishaku.readthedocs.io/en/latest/cog.html


class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    @Feature.Command(parent="jsk", name="py", aliases=["python"])
    async def jsk_python(self, ctx: commands.Context, *, argument: codeblock_converter):
        arg_dict = get_var_dict_from_ctx(ctx, "")
        arg_dict.update(get_var_dict_from_ctx(ctx, "_"))
        arg_dict["_"] = self.last_result

        if ctx.message.reference and isinstance(ctx.message.reference.resolved, discord.Message):
            resolved_msg = ctx.message.reference.resolved
            arg_dict.update(r=resolved_msg, _r=resolved_msg)

        scope = self.scope

        try:
            async with ReplResponseReactor(ctx.message):
                with self.submit(ctx):
                    executor = AsyncCodeExecutor(argument.content, scope, arg_dict=arg_dict)
                    async for send, result in AsyncSender(executor):
                        if result is None:
                            continue

                        self.last_result = result

                        send(await self.jsk_python_result_handling(ctx, result))

        finally:
            scope.clear_intersection(arg_dict)


async def setup(bot: commands.Bot):
    await bot.add_cog(Jishaku(bot=bot))
